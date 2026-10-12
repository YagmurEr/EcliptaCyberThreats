# Claude Code için kurulum talimatı — eclipta.tr/SiberGundem

Bu dosyayı Claude Code'a vererek kurulumu yaptırabilirsiniz:
> "CLAUDE_CODE_KURULUM.md dosyasındaki adımları uygula."

## Mimari
- **Veri (bu depo):** GitHub Actions her gün KEV + EPSS + CVSS ve RSS haberlerini çeker, `docs/data/*.json` olarak depoya işler. GitHub Pages bu klasörü `https://<kullanici>.github.io/tehdit-veri/data/` adresinden yayınlar.
- **Sayfa (eclipta.tr):** `web/tehdit/index.html (SiberGündem sayfası)` bir kez `eclipta.tr/SiberGundem/` klasörüne yüklenir; her açılışta veriyi GitHub Pages'ten okur.

## Adımlar (Claude Code)
1. `gh auth status` ile GitHub oturumunu doğrula. Oturum yoksa kullanıcıdan `gh auth login` çalıştırmasını iste; parola veya erişim anahtarı **isteme**.
2. GitHub kullanıcı adını al: `gh api user -q .login` → `KULLANICI`.
3. `web/tehdit/index.html (SiberGündem sayfası)` içindeki `GITHUB_KULLANICI` ifadesini `KULLANICI` ile değiştir.
4. Depoyu oluştur ve gönder:
   ```bash
   git init -b main && git add . && git commit -m "İlk kurulum"
   gh repo create tehdit-veri --public --source . --push
   ```
5. Actions'a yazma izni ver:
   ```bash
   gh api -X PUT repos/KULLANICI/tehdit-veri/actions/permissions/workflow -f default_workflow_permissions=write
   ```
6. GitHub Pages'i `main` dalı `/docs` klasöründen aç:
   ```bash
   gh api -X POST repos/KULLANICI/tehdit-veri/pages -f "source[branch]=main" -f "source[path]=/docs"
   ```
7. İş akışını elle tetikle ve sonucunu izle:
   ```bash
   gh workflow run "Veri güncelle" && sleep 10 && gh run watch
   ```
   `haberler_otomatik.json` içindeki `kaynakDurumu` alanında hata veren RSS kaynağı varsa kullanıcıya bildir.
8. Birkaç dakika sonra `https://KULLANICI.github.io/tehdit-veri/data/kev.json` adresinin açıldığını doğrula.
9. Kullanıcıya şunları hatırlat:
   - `web/tehdit/index.html (SiberGündem sayfası)` dosyasını FTP ile `eclipta.tr/SiberGundem/index.html` olarak yüklemesi.
   - Sitede Content-Security-Policy varsa `connect-src` yönergesine `https://KULLANICI.github.io` eklemesi.
   - Sayfayı menüye ve sitemap'e eklemesi.

## Güncelleme rehberi (kurulumdan sonra)
| Ne | Nasıl | Sıklık |
|---|---|---|
| KEV, EPSS, CVSS | Otomatik (her gün 06:15 TSİ) | — |
| RSS haberleri | Otomatik (günde 4 kez) | — |
| Türkçe özetli haberler | GitHub web arayüzünde `docs/data/haberler_manuel.json` düzenle | İstediğiniz zaman |
| KVKK ilan günleri | `docs/data/kvkk_ilan.json` dosyasına satır ekle | Her çarşamba ilanından sonra |
| KVKK öne çıkan bildirimler | `docs/data/kvkk_bildirim.json` dosyasına kayıt ekle | Haftalık |
| İzlenen marka ekle/çıkar | `config/izleme.json` | Gerektiğinde |
| RSS kaynağı ekle | `config/kaynaklar.json` | Gerektiğinde |

JSON dosyaları GitHub web arayüzünde (kalem simgesi) doğrudan düzenlenebilir; kaydettiğinizde birkaç dakika içinde sayfaya yansır. FTP gerekmez.
