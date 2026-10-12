# tehdit-veri — Eclipta Küresel Tehdit İstihbaratı veri deposu

eclipta.tr/SiberGundem sayfasının veri kaynağıdır. Kurulum ve güncelleme rehberi için `CLAUDE_CODE_KURULUM.md` dosyasına bakın.

- `scripts/fetch_kev.py` — CISA KEV + FIRST EPSS + CVSS (günlük)
- `scripts/fetch_news.py` — RSS haber başlıkları (günde 4 kez)
- `docs/data/` — sayfanın okuduğu JSON dosyaları (GitHub Pages ile yayınlanır)
- `config/` — izlenen markalar ve haber kaynakları
- `web/tehdit/index.html` — eclipta.tr/SiberGundem/ klasörüne bir kez yüklenecek sayfa

Kaynak verilerin lisans ve kullanım koşulları ilgili kuruluşlara aittir (CISA, FIRST, CVE Program). Haber akışında yalnızca başlık, bağlantı ve tarih saklanır.
