#!/usr/bin/env python3
"""config/kaynaklar.json'daki RSS/Atom akışlarından başlık, bağlantı ve tarih toplar;
izlenen markalara göre gruplayıp docs/data/haberler_otomatik.json dosyasına yazar.

Yalnızca başlık, bağlantı, kaynak adı ve tarih saklanır; makale metni kopyalanmaz.
Erişilemeyen kaynak iş akışını durdurmaz.
"""
import datetime as dt
import email.utils
import hashlib
import json
import pathlib
import re
import sys
import urllib.request
try:
    import defusedxml.ElementTree as ET  # XXE koruması
except ImportError:
    import xml.etree.ElementTree as ET  # defusedxml yoksa stdlib (XXE riski düşük: harici varlık çözülmez)

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"
IZLEME = json.loads((ROOT / "config" / "izleme.json").read_text(encoding="utf-8"))
KAYNAK = json.loads((ROOT / "config" / "kaynaklar.json").read_text(encoding="utf-8"))
HEADERS = {"User-Agent": "eclipta-tehdit-veri/1.0 (+https://eclipta.tr/SiberGundem)"}
ATOM = "{http://www.w3.org/2005/Atom}"
MAX_BOYUT = 5 * 1024 * 1024


def tarih_coz(s):
    if not s:
        return None
    s = s.strip()
    try:
        return email.utils.parsedate_to_datetime(s).astimezone(dt.timezone.utc)
    except Exception:
        pass
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return None


def temiz(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()[:300]


def akis_oku(kaynak):
    url = kaynak["url"]
    if not url.startswith("https://"):
        raise ValueError("Yalnızca https:// adresleri desteklenir: " + url)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        ham = r.read(MAX_BOYUT + 1)
    if len(ham) > MAX_BOYUT:
        raise ValueError("akış boyutu sınırı aşıldı")
    kok = ET.fromstring(ham)  # stdlib ayrıştırıcısı harici varlık (XXE) çözmez
    ogeler = []
    for it in kok.iter("item"):  # RSS 2.0
        ogeler.append((it.findtext("title"), it.findtext("link"), it.findtext("pubDate")))
    for it in kok.iter(ATOM + "entry"):  # Atom
        link = None
        for l in it.findall(ATOM + "link"):
            if l.get("rel", "alternate") == "alternate":
                link = l.get("href")
        ogeler.append((it.findtext(ATOM + "title"), link, it.findtext(ATOM + "updated") or it.findtext(ATOM + "published")))
    sonuc = []
    for baslik, link, tarih in ogeler:
        baslik, link, t = temiz(baslik), (link or "").strip(), tarih_coz(tarih)
        if not baslik or not link.startswith("https://") or not t:
            continue
        sonuc.append({
            "id": hashlib.sha1(link.encode("utf-8"), usedforsecurity=False).hexdigest()[:12],
            "tarih": t.date().isoformat(), "kaynak": kaynak["ad"], "baslik": baslik, "url": link,
        })
    return sonuc


def grupla(baslik):
    b = baslik.lower()
    for g in IZLEME["gruplar"]:
        if any(k.lower() in b for k in g.get("anahtarKelimeler", [])):
            return g["ad"]
    return "Genel"


def main():
    yol = DATA / "haberler_otomatik.json"
    eski = json.loads(yol.read_text(encoding="utf-8")).get("haberler", []) if yol.exists() else []
    hepsi = {h["id"]: h for h in eski}
    durum = []
    for k in KAYNAK["kaynaklar"]:
        if not k.get("aktif", True):
            continue
        try:
            yeni = akis_oku(k)
            for h in yeni:
                h["grup"] = grupla(h["baslik"])
                hepsi[h["id"]] = h
            durum.append({"kaynak": k["ad"], "durum": "ok", "adet": len(yeni)})
        except Exception as e:
            print(f"UYARI: {k['ad']} okunamadı: {e}", file=sys.stderr)
            durum.append({"kaynak": k["ad"], "durum": "hata"})

    esik = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=KAYNAK.get("saklamaGunu", 45))).date().isoformat()
    liste = sorted((h for h in hepsi.values() if h["tarih"] >= esik), key=lambda h: (h["tarih"], h["id"]), reverse=True)
    genel, sonuc = 0, []
    for h in liste:
        if h["grup"] == "Genel":
            genel += 1
            if genel > KAYNAK.get("genelHaberLimiti", 40):
                continue
        sonuc.append(h)

    yol.write_text(json.dumps({
        "guncelleme": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "kaynakDurumu": durum, "haberler": sonuc,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(sonuc)} haber yazıldı; kaynaklar: " + ", ".join(f"{d['kaynak']}={d['durum']}" for d in durum))


if __name__ == "__main__":
    main()
