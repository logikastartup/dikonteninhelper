# Dikontenin Helper

Aplikasi Dikontenin Helper adalah aplikasi pembantu yang dirancang untuk mengumpulkan sumber dari situs web yang diinginkan untuk Dikontenin.

---

## Update Fitur

- **Antarmuka Berbasis Web**: Dashboard yang intuitif untuk mengelola sumber
- **Crawling yang Powerful**: Ekstraksi konten menggunakan Selenium WebDriver
- **Ekstraksi Konten**: Membersihkan dan mengekstrak konten utama dari halaman web
- **Caching Pintar**: Caching yang dapat dikonfigurasi untuk menghindari crawling ulang
- **Pencarian & Penyaringan**: Cepat menemukan sumber yang sudah di-crawl berdasarkan URL atau judul
- **Operasi Massal**: Pilih dan salin beberapa sumber sekaligus
- **API RESTful**: Akses terprogram ke semua fungsionalitas
- **Desain Responsif**: Berfungsi pada perangkat desktop dan tablet

---

## Persyaratan

- Python 3.12+
- Browser Chrome atau Firefox
- Paket Python yang diperlukan (lihat requirements.txt)
- Google Chrome (untuk Selenium WebDriver)

---

## Instalasi

1. Clone repository:
   ```bash
   git clone <repository-url>
   cd dikonteninhelper
   python -m venv .venv
   pip install -r requirements.txt
   ```

2. Buat dan aktifkan lingkungan virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Di Windows
   source .venv/bin/activate  # Di Unix/Linux/MacOS
   ```

3. Konfigurasikan aplikasi dengan mengedit `config.ini` jika diperlukan.

4. Jalankan aplikasi:
   ```bash
   python main_gui.py
   ```

5. Akses antarmuka web di: http://localhost:8000

---

## Konfigurasi

Edit `config.ini` untuk menyesuaikan perilaku aplikasi:

```ini
[server]
host = 127.0.0.1  # Host server
port = 4477       # Port server

[storage]
save_folder = data              # Folder untuk menyimpan file data
database_path = data/crawled_data.db  # Jalur database SQLite

[crawler]
browser_timeout = 60   # Batas waktu browser Selenium dalam detik
skip_crawl_time = 60    # Hari sebelum melakukan crawling ulang URL
sleep_time = 3          # Waktu tunggu untuk pemuatan halaman
browser_path =          # Opsional: Jalur ke binary Chrome/Firefox
```

---

## Lisensi

Dikontenin Helper berlisensi  [MIT](https://opensource.org/license/mit)

---

## Bantuan

**[Dikontenin](https://dikontenin.com)** adalah aplikasi pembuat konten berbahasa Indonesia dan Inggris yang dirancang untuk membantu Anda menyusun artikel berkualitas tinggi dalam waktu singkat. Dikontenin memfasilitasi proses kreatif dengan menyediakan kerangka dan draf awal yang bisa Anda kembangkan sesuai gaya dan kebutuhan.

👉 Untuk bantuan, kunjungi [**Dikontenin.com**](https://dikontenin.com)