# SiberGündem – Açık Veri Arayüzü (Statik JSON)

Bu proje bir REST API sunucusu çalıştırmaz. GitHub Pages üzerinden **herkese açık, yalnızca okunabilir JSON dosyaları** sunar.

Temel adres: `https://YagmurEr.github.io/EcliptaCyberThreats/data/`

## Veri uç noktaları

| Dosya | İçerik | Temel alanlar |
| --- | --- | --- |
| [kev.json](https://YagmurEr.github.io/EcliptaCyberThreats/data/kev.json) | İzlenen üreticilerin CISA KEV kayıtları, EPSS ve CVSS zenginleştirmesi | `guncelleme`, `katalogTarih`, `epssTarih`, `gruplar[]`, `kayitlar[]`, `aylik[]` |
| [aktif_istismar.json](https://YagmurEr.github.io/EcliptaCyberThreats/data/aktif_istismar.json) | Derlenmiş aktif istismar verileri | Şema için güncel JSON dosyasına bakın |
| [kvkk_bildirim.json](https://YagmurEr.github.io/EcliptaCyberThreats/data/kvkk_bildirim.json) | KVKK veri ihlali bildirimleri | `aciklama`, `bildirimler[]` |
| [kvkk_ilan.json](https://YagmurEr.github.io/EcliptaCyberThreats/data/kvkk_ilan.json) | İlan günleri ve özetler | `ilanlar[]` |
| [haberler_manuel.json](https://YagmurEr.github.io/EcliptaCyberThreats/data/haberler_manuel.json) | Editoryal haber seçkisi | `haberler[]` |
| [haberler_otomatik.json](https://YagmurEr.github.io/EcliptaCyberThreats/data/haberler_otomatik.json) | Otomatik RSS/Atom haber derlemesi | `guncelleme`, `kaynakDurumu[]`, `haberler[]` |
| [cvss_onbellek.json](https://YagmurEr.github.io/EcliptaCyberThreats/data/cvss_onbellek.json) | Dahili CVSS önbelleği | Şema ve içerik değişebilir; kararlı API değildir |

## Örnek alanlar

`kev.json > kayitlar[]`: `cveID`, `grup`, `uretici`, `urun`, `zafiyet`, `eklenme`, `sonTarih`, `fidye`, `epssYuzde`, `epssYuzdelik`, `cvss`.

`kvkk_bildirim.json > bildirimler[]`: `id`, `tarih`, `veriSorumlusu`, `sektor`, `tur`, `etkilenen`, `etkilenenNot`, `veriKategorileri`, `veriDetay`, `karar`, `url`.

`haberler_otomatik.json > haberler[]`: `id`, `tarih`, `kaynak`, `baslik`, `url`, `grup` ve varsa `ozet`.

**Önemli:** `epssYuzde` yüzde birimindedir (ör. `12.5` = %12,5). Eksik skor ve etkilenen kişi sayıları `null` olabilir. `sonTarih` CISA'nın ABD federal kurumlarına ilişkin düzeltme tarihidir; Türkiye'deki kurumlar açısından yasal son tarih değildir. Alanların varlığı, veri doğruluğu ve arşiv bütünlüğü garanti edilmez.

## Kullanım

```bash
curl -fsSL https://YagmurEr.github.io/EcliptaCyberThreats/data/kev.json -o kev.json
curl -fsSL https://YagmurEr.github.io/EcliptaCyberThreats/data/kvkk_bildirim.json -o kvkk.json
```

Python 3 – en yüksek EPSS skoruna sahip ilk 5 kayıt:

```python
import json
from urllib.request import urlopen

url = "https://YagmurEr.github.io/EcliptaCyberThreats/data/kev.json"
with urlopen(url, timeout=15) as response:
    data = json.load(response)
rows = sorted(
    (x for x in data["kayitlar"] if x.get("epssYuzde") is not None),
    key=lambda x: x["epssYuzde"],
    reverse=True,
)
for item in rows[:5]:
    print(item["cveID"], item["grup"], item["epssYuzde"])
```

Splunk veya Elastic tarafında da JSON dosyaları zamanlanmış bir ingest işlemiyle alınabilir. Bu URL'ler kimlik doğrulama, sürümleme, SLA veya sorgu parametresi sağlamaz; istemci önbelleklemesi ve oran sınırlaması uygulanması önerilir.

## RSS

`https://YagmurEr.github.io/EcliptaCyberThreats/rss.xml`

RSS başlıkları kamuya açık kaynaklardan derlenir. Haberlerin asıl içeriği ilgili yayıncıya aittir. Besleme zamanlanmış veri güncellemesi sırasında yenilenir.

## Kaynak / sınırlamalar

- KEV: CISA Known Exploited Vulnerabilities.
- EPSS: FIRST Exploit Prediction Scoring System.
- CVSS: ilgili kaynaklardan elde edilen metrikler.
- KVKK: resmî Kurum ilanları ve açıklamada belirtilen derlemeler.
- İstatistikler bir siber risk değerlendirmesinin yerine geçmez.
- USOM: resmî [USOM zafiyet sayfası](https://www.usom.gov.tr/zafiyet) API tabanlı erişimi işaret ediyor; veri sözleşmesi, erişim koşulları, yetkilendirme ve CVE eşlemesi doğrulanmadan otomatik veri toplama eklenmedi.
- JSON erişimi herkese açık olmakla birlikte, kaynakların telif ve yeniden dağıtım koşulları ayrıca geçerlidir.
