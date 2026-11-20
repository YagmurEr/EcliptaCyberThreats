"""Ağ bağlantısı kullanmayan KEV ve RSS birim testleri."""
import importlib.util
import io
import gzip
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kev = load("fetch_kev")
news = load("fetch_news")


class KevTests(unittest.TestCase):
    def test_rejects_http(self):
        with self.assertRaises(ValueError):
            kev.get("http://example.com")

    def test_invalid_cve_not_fetched(self):
        with patch.object(kev, "get") as request:
            self.assertIsNone(kev.cvss_cek("invalid"))
            request.assert_not_called()

    def test_epss_csv(self):
        today = kev.dt.datetime.now(kev.dt.timezone.utc).date()
        csv_data = b"#model_version:x,score_date:y\ncve,epss,percentile\nCVE-2025-1234,0.12,0.95\n"
        with patch.object(kev, "get", return_value=gzip.compress(csv_data)):
            date, result = kev.epss_yukle({"CVE-2025-1234"})
        self.assertEqual(date, today.isoformat())
        self.assertEqual(result["CVE-2025-1234"], (0.12, 0.95))


class NewsTests(unittest.TestCase):
    def test_date(self):
        self.assertEqual(news.tarih_coz("2026-11-20T10:00:00Z").date().isoformat(), "2026-11-20")
        self.assertIsNone(news.tarih_coz("not a date"))

    def test_clean(self):
        self.assertEqual(news.temiz("<b>Hello</b>   world"), "Hello world")

    def test_rejects_http_feed(self):
        with self.assertRaises(ValueError):
            news.akis_oku({"url": "http://example.com/feed", "ad": "Test"})

    def test_parse_rss(self):
        payload = b'<rss><channel><item><title>Test news</title><link>https://example.com/article</link><pubDate>Fri, 20 Nov 2026 09:00:00 GMT</pubDate></item></channel></rss>'
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, n): return payload
        with patch.object(news.urllib.request, "urlopen", return_value=FakeResponse()):
            rows = news.akis_oku({"url": "https://example.com/rss", "ad": "Example"})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tarih"], "2026-11-20")


if __name__ == "__main__":
    unittest.main()
