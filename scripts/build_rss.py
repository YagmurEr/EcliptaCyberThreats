#!/usr/bin/env python3
"""Mevcut haber JSON'larından güvenli, statik RSS 2.0 beslemesi oluşturur."""
import datetime as dt
import email.utils
import json
import pathlib
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"
SITE = "https://eclipta.tr/SiberGundem/"
FEED = "https://YagmurEr.github.io/EcliptaCyberThreats/rss.xml"
MAX_ITEMS = 60


def load_items(filename):
    obj = json.loads((DATA / filename).read_text(encoding="utf-8"))
    return obj.get("haberler", [])


def valid_url(url):
    if not isinstance(url, str):
        return False
    p = urlsplit(url)
    return p.scheme == "https" and bool(p.hostname) and not p.username and not p.password


def valid_day(value):
    try:
        return dt.date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def build():
    unique = {}
    for filename in ("haberler_otomatik.json", "haberler_manuel.json"):
        for entry in load_items(filename):
            url = entry.get("url")
            date = valid_day(entry.get("tarih"))
            if valid_url(url) and date and entry.get("baslik"):
                unique.setdefault(url, (date, entry))
    sorted_items = sorted(unique.values(), key=lambda row: (row[0], row[1].get("baslik", "")), reverse=True)[:MAX_ITEMS]

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    for key, value in [
        ("title", "Eclipta SiberGündem"),
        ("link", SITE),
        ("description", "Siber güvenlik gelişmeleri ve zafiyet haberleri; kaynak bağlantılarıyla."),
        ("language", "tr-TR"),
        ("generator", "EcliptaCyberThreats scripts/build_rss.py"),
        ("atom:link", None),
    ]:
        if value is not None:
            ET.SubElement(channel, key).text = value
    atom = "{http://www.w3.org/2005/Atom}"
    ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
    ET.SubElement(channel, atom + "link", {"href": FEED, "rel": "self", "type": "application/rss+xml"})
    ET.SubElement(channel, "lastBuildDate").text = email.utils.format_datetime(dt.datetime.now(dt.timezone.utc))
    for date, entry in sorted_items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = str(entry["baslik"])[:300]
        ET.SubElement(item, "link").text = entry["url"]
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = entry["url"]
        desc = entry.get("ozet") or ("Kaynak: " + str(entry.get("kaynak", "Bilinmiyor")))
        ET.SubElement(item, "description").text = str(desc)[:300]
        published = dt.datetime.combine(date, dt.time.min, dt.timezone.utc)
        ET.SubElement(item, "pubDate").text = email.utils.format_datetime(published)
    out = ROOT / "docs" / "rss.xml"
    out.write_bytes(ET.tostring(rss, encoding="utf-8", xml_declaration=True))
    # Üretilen XML'i yeniden ayrıştır: en azından yapısal doğrulama
    ET.parse(out)
    print("RSS oluşturuldu:", out, "kayıt:", len(sorted_items))


if __name__ == "__main__":
    build()
