#!/usr/bin/env python3
"""CISA KEV kataloğunu EPSS ve CVSS ile zenginleştirip docs/data/kev.json dosyasını üretir.

Kaynaklar (hepsi herkese açık, kimlik doğrulama gerektirmez):
  - CISA KEV: github.com/cisagov/kev-data
  - EPSS (FIRST, günlük): github.com/empiricalsec/epss_scores
  - CVSS: github.com/CVEProject/cvelistV5 (yalnızca izlenen kayıtlar, önbellekli)
"""
import csv
import datetime as dt
import gzip
import io
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"
CFG = json.loads((ROOT / "config" / "izleme.json").read_text(encoding="utf-8"))

KEV_URL = "https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json"
EPSS_URL = "https://raw.githubusercontent.com/empiricalsec/epss_scores/main/{y}/epss_scores-{d}.csv.gz"
CVE_URL = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/{y}/{grp}/{cve}.json"
HEADERS = {"User-Agent": "eclipta-tehdit-veri/1.0 (+https://eclipta.tr/SiberGundem)"}
CVE_RE = re.compile(r"^CVE-(\d{4})-(\d{4,})$")


def get(url, timeout=60, tries=3):
    if not url.startswith("https://"):
        raise ValueError("Yalnızca https:// adresleri desteklenir: " + url)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:  # nosec B310
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            last = e
        except Exception as e:  # ağ hatası: kısa bekleyip yeniden dene
            last = e
        time.sleep(2 * (i + 1))
    raise last


def grup_bul(kayit):
    metin = " ".join([kayit.get("vendorProject", ""), kayit.get("product", ""), kayit.get("vulnerabilityName", "")]).lower()
    for g in CFG["gruplar"]:
        if kayit.get("vendorProject", "").strip() in g.get("ureticiler", []):
            return g["ad"]
        if g.get("metin") and g["metin"].lower() in metin:
            return g["ad"]
    return None


def epss_yukle(cveler):
    """Son 7 gün içindeki en güncel EPSS dosyasını bulur; yalnızca istenen CVE'leri döndürür."""
    bugun = dt.datetime.now(dt.timezone.utc).date()
    for geri in range(0, 7):
        gun = bugun - dt.timedelta(days=geri)
        url = EPSS_URL.format(y=gun.year, d=gun.isoformat())
        try:
            ham = get(url, timeout=120)
        except urllib.error.HTTPError:
            continue
        sonuc = {}
        with gzip.open(io.BytesIO(ham), "rt", encoding="utf-8") as f:
            ilk = f.readline()  # '#model_version:...,score_date:...' satırı
            if not ilk.startswith("#"):
                f = io.StringIO(ilk + f.read())
            for satir in csv.DictReader(f):
                if satir["cve"] in cveler:
                    sonuc[satir["cve"]] = (float(satir["epss"]), float(satir["percentile"]))
        return gun.isoformat(), sonuc
    print("UYARI: Son 7 güne ait EPSS dosyası bulunamadı", file=sys.stderr)
    return None, {}


def cvss_cek(cve):
    m = CVE_RE.match(cve)
    if not m:
        return None
    yil, num = m.group(1), m.group(2)
    grp = (num[:-3] if len(num) > 3 else "0") + "xxx"
    try:
        d = json.loads(get(CVE_URL.format(y=yil, grp=grp, cve=cve), timeout=30))
    except Exception:
        return None
    konteyner = [d.get("containers", {}).get("cna", {})] + d.get("containers", {}).get("adp", [])
    v4 = None
    for c in konteyner:
        for metr in c.get("metrics", []):
            for k in ("cvssV3_1", "cvssV3_0"):
                if k in metr and "baseScore" in metr[k]:
                    return float(metr[k]["baseScore"])
            if "cvssV4_0" in metr and "baseScore" in metr["cvssV4_0"] and v4 is None:
                v4 = float(metr["cvssV4_0"]["baseScore"])
    return v4


def main():
    kev = json.loads(get(KEV_URL))
    tum = kev["vulnerabilities"]
    ref = max(k["dateAdded"] for k in tum)

    izlenen = []
    for k in tum:
        g = grup_bul(k)
        if g:
            izlenen.append({
                "cveID": k["cveID"], "grup": g, "uretici": k["vendorProject"].strip(), "urun": k["product"].strip(),
                "zafiyet": k["vulnerabilityName"].strip(), "eklenme": k["dateAdded"], "sonTarih": k["dueDate"],
                "fidye": "Biliniyor" if k.get("knownRansomwareCampaignUse") == "Known" else "Bilinmiyor",
            })

    epss_tarih, epss = epss_yukle({k["cveID"] for k in izlenen})

    onbellek_yolu = DATA / "cvss_onbellek.json"
    onbellek = json.loads(onbellek_yolu.read_text(encoding="utf-8")) if onbellek_yolu.exists() else {}
    eksik = [k["cveID"] for k in izlenen if k["cveID"] not in onbellek]
    for cve in eksik:
        skor = cvss_cek(cve)
        if skor is not None:
            onbellek[cve] = skor
    onbellek_yolu.write_text(json.dumps(onbellek, ensure_ascii=False, sort_keys=True), encoding="utf-8")

    for k in izlenen:
        e = epss.get(k["cveID"])
        k["epssYuzde"] = round(e[0] * 100, 1) if e else None
        k["epssYuzdelik"] = round(e[1] * 100, 1) if e else None
        k["cvss"] = onbellek.get(k["cveID"])
    izlenen.sort(key=lambda k: (k["eklenme"], k["cveID"]), reverse=True)

    # Son 24 ay: tüm katalog ve izlenen kayıtlar
    y, m = int(ref[:4]), int(ref[5:7])
    aylar = []
    for _ in range(24):
        aylar.insert(0, f"{y}-{m:02d}")
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    aylik = [{
        "ay": a,
        "eklenen": sum(1 for k in tum if k["dateAdded"].startswith(a)),
        "izlenen": sum(1 for k in izlenen if k["eklenme"].startswith(a)),
    } for a in aylar]

    cikti = {
        "guncelleme": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "katalogSurum": kev.get("catalogVersion"),
        "katalogTarih": ref,
        "epssTarih": epss_tarih,
        "toplam": len(tum),
        "gruplar": [{"ad": g["ad"], "renk": g["renk"], "altBaslik": g.get("altBaslik", "")} for g in CFG["gruplar"]],
        "aylik": aylik,
        "kayitlar": izlenen,
    }
    (DATA / "kev.json").write_text(json.dumps(cikti, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"KEV {cikti['katalogSurum']}: {len(tum)} kayıt, {len(izlenen)} izlenen; EPSS {epss_tarih}; "
          f"CVSS eksik {sum(1 for k in izlenen if k['cvss'] is None)}")


if __name__ == "__main__":
    main()
