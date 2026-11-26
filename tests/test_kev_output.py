import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class KevOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs" / "data" / "kev.json").read_text(encoding="utf-8"))
        cls.rows = cls.data["kayitlar"]

    def test_genel_liste_tum_katalogu_kapsar(self):
        self.assertEqual(len(self.rows), self.data["toplam"])
        self.assertEqual(len({row["cveID"] for row in self.rows}), self.data["toplam"])

    def test_25_kasimda_eklenen_on_kayit_listede(self):
        rows = [row for row in self.rows if row["eklenme"] == "2026-11-25"]
        self.assertEqual(len(rows), 10)

    def test_cvss_epss_eksikleri_gecerli_null_degerlerdir(self):
        for row in self.rows:
            self.assertTrue(row["cvss"] is None or isinstance(row["cvss"], (int, float)))
            self.assertTrue(row["epssYuzde"] is None or isinstance(row["epssYuzde"], (int, float)))

    def test_varsayilan_siralama_yeniden_eskiye(self):
        keys = [(row["eklenme"], row["cveID"]) for row in self.rows]
        self.assertEqual(keys, sorted(keys, reverse=True))


if __name__ == "__main__":
    unittest.main()
