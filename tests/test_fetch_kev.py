import importlib.util
import pathlib
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fetch_kev", ROOT / "scripts" / "fetch_kev.py")
fetch_kev = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetch_kev)


def cisa_kaydi(vendor="Örnek Üretici", cve="CVE-2026-99999"):
    return {
        "cveID": cve,
        "vendorProject": vendor,
        "product": "Örnek Ürün",
        "vulnerabilityName": "Örnek Zafiyet",
        "dateAdded": "2026-11-25",
        "dueDate": "2026-12-16",
        "knownRansomwareCampaignUse": "Unknown",
    }


class FetchKevTests(unittest.TestCase):
    def test_kartsiz_uretici_genel_kayitta_kalir(self):
        kayit = fetch_kev.kayit_olustur(cisa_kaydi())
        self.assertIsNone(kayit["grup"])
        self.assertEqual(kayit["uretici"], "Örnek Üretici")

    def test_tanimli_uretici_karti_korunur(self):
        kayit = fetch_kev.kayit_olustur(cisa_kaydi(vendor="Cisco"))
        self.assertEqual(kayit["grup"], "Cisco")

    def test_cvss_eksigi_null_kalabilir(self):
        kayitlar = [fetch_kev.kayit_olustur(cisa_kaydi())]
        with mock.patch.object(fetch_kev, "cvss_cek", return_value=None):
            onbellek = fetch_kev.cvss_onbellegini_tamamla(kayitlar, {})
        self.assertNotIn("CVE-2026-99999", onbellek)


if __name__ == "__main__":
    unittest.main()
