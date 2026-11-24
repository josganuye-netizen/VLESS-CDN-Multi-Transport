# VLESS Argo Multi-Transport Generator

Panel generator akun **VLESS CDN (Argo Tunnel)** ringan berbasis **Xray-core**, **Cloudflared**, dan **Python Web UI**. Mendukung tiga jenis transport sekaligus dalam satu container serta memungkinkan pengguna memasukkan domain atau bug host mereka sendiri saat membuat akun.

## Fitur Utama

* **3 Protokol Transport Sekaligus:**
  * **XHTTP (`mode: auto`)** — Path `/xhttp` (Port internal `8080`)
  * **HTTPUpgrade** — Path `/httpup` (Port internal `8081`)
  * **WebSocket (WS)** — Path `/vless` (Port internal `8082`)
* **Dukungan Multi-Port:** Otomatis menghasilkan link konfigurasi untuk **TLS (`443`)** dan **Non-TLS (`80`)**.
* **Custom Domain Mandiri:** Pengunjung dapat mengisi nama akun dan domain/host masing-masing secara langsung melalui Web UI.
* **Auto-Reload Xray:** Setiap pembuatan akun baru otomatis memperbarui `config.json` dan memuat ulang service Xray tanpa memutus tunnel.

---

## Persiapan & Deployment

### 1. Deploy ke Railway (Docker)
1. Fork atau clone repository ini ke akun GitHub kamu.
2. Buat project baru di **Railway** → pilih **Deploy from GitHub repo**.
3. Masuk ke tab **Variables** dan tambahkan token Cloudflare Tunnel milikmu:
   * `CF_TOKEN` = `<token_cloudflare_tunnel_kamu>`

### 2. Konfigurasi Rute di Cloudflare Zero Trust
Buka **Cloudflare Zero Trust** → **Networks** → **Tunnels** → pilih tunnel aktif → tab **Routes**, lalu tambahkan rute berikut (isi kolom **Path** tanpa tanda `/` di depan):

| Subdomain | Domain | Path | Type | URL |
| :--- | :--- | :--- | :--- | :--- |
| `vpn` | `domainkamu.com` | `xhttp` | `HTTP` | `http://127.0.0.1:8080` |
| `vpn` | `domainkamu.com` | `httpup` | `HTTP` | `http://127.0.0.1:8081` |
| `vpn` | `domainkamu.com` | `vless` | `HTTP` | `http://127.0.0.1:8082` |
| `panel` *(opsional)* | `domainkamu.com` | *(kosong)* | `HTTP` | `http://127.0.0.1:2053` |

*(Jika tidak membuat rute subdomain untuk port `2053`, Web UI tetap bisa diakses melalui domain bawaan `.up.railway.app` dari tab **Settings → Networking** di Railway).*

### 3. Pengaturan Jaringan di Dashboard Cloudflare
Agar seluruh protokol dan port berjalan lancar, buka dashboard **Cloudflare** pada domain yang digunakan:
1. **Network:**
   * **WebSockets** → **ON**
   * **HTTP/2 to Origin** → **ON**
2. **SSL/TLS → Overview:**
   * Pilih mode **Full** atau **Flexible**.
3. **SSL/TLS → Edge Certificates:**
   * **Always Use HTTPS** → **OFF** *(wajib dimatikan jika ingin menggunakan jalur Non-TLS Port `80`)*.

---

## Cara Penggunaan (Untuk Pengguna)

1. Buka halaman **VLESS Account Generator**.
2. Masukkan **Nama Akun** (maksimal 20 karakter huruf/angka).
3. Masukkan **Domain** atau host CDN yang sudah terhubung ke tunnel (contoh: `vpn.domainkamu.com`).
4. Klik tombol **+ Buat Akun**.
5. Pilih dan salin link sesuai kebutuhan klien:
   * **TLS Port 443:** `XHTTP 443`, `HTTPUp 443`, atau `WS 443`
   * **Non-TLS Port 80:** `XHTTP 80`, `HTTPUp 80`, atau `WS 80`
6. Impor link ke aplikasi klien VPN (**v2rayNG**, **Sing-box**, **Hiddify**, **HTTP Custom**, atau klien sejenis) dan jalankan.

> **Catatan Klien:** Protokol **XHTTP** membutuhkan aplikasi klien versi terbaru (seperti v2rayNG / Sing-box / Hiddify terbaru). Untuk klien versi lama, gunakan jalur **HTTPUp** atau **WS**.
