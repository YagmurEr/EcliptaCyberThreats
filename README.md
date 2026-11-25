# tehdit-veri — Eclipta Küresel Tehdit İstihbaratı veri deposu

[`eclipta.tr/sibergundem`](https://eclipta.tr/sibergundem) sayfasının açık veri kaynağıdır. Kurulum ve güncelleme rehberi için `CLAUDE_CODE_KURULUM.md` dosyasına bakın.

- `scripts/fetch_kev.py` — CISA KEV + FIRST EPSS + CVSS (günlük)
- `scripts/fetch_news.py` — RSS haber başlıkları (günde 4 kez)
- `docs/data/` — sayfanın okuduğu JSON dosyaları (GitHub Pages ile yayınlanır)
- `config/` — izlenen markalar ve haber kaynakları
- `web/tehdit/index.html` — eski, bağımsız dağıtım şablonu; canlı arayüzün kaynağı değildir

## Kaynak sınırı

Canlı arayüzün tek kanonik kaynağı Eclipta kurumsal site projesidir. Bu depo yalnızca açık veri/API, veri üretim betikleri ve eski bağımsız dağıtım şablonunu içerir. Böylece arayüz değişiklikleri iki farklı depoda sürüklenmez; canlı SiberGündem her zaman küçük harfli [`/sibergundem`](https://eclipta.tr/sibergundem) yolundan veriyi bu depodan okur.

## Lisans

Bu depodaki Eclipta tarafından yazılmış kod, yapılandırma ve dokümantasyon [MIT License](LICENSE) ile lisanslanmıştır.

`docs/data/` altındaki çıktılar; CISA KEV, FIRST EPSS ve CVE Programı gibi üçüncü taraf kaynaklardan türetilir. Bu kaynakların kendi lisansları ve kullanım koşulları geçerlidir; bu depo, onlara ilişkin ek bir lisans vermez. Haber akışında yalnızca başlık, bağlantı ve tarih saklanır.


