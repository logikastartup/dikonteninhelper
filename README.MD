# Dikontenin Helper

## 🚀 Apa Itu Dikontenin?

**[Dikontenin](https://dikontenin.com)** adalah platform AI content generator berbahasa Indonesia yang dirancang untuk mempermudah siapa pun—dari pelaku bisnis, digital marketer, hingga content creator—dalam membuat artikel berkualitas tinggi, SEO-friendly, dan siap publish hanya dengan memasukkan keyword.

Tanpa perlu repot riset panjang atau bayar penulis mahal, semua bisa dikerjakan otomatis dalam hitungan menit.

---

## ✨ Kenapa Harus Pakai Dikontenin?

Dengan Dikontenin, kamu bisa:

* 🧠 **Generate Artikel Otomatis:** Cukup masukkan keyword, AI akan menulis artikel lengkap secara otomatis.
* 🔍 **Riset Keyword Otomatis:** Temukan keyword potensial untuk mendongkrak traffic secara instan.
* ✍️ **Artikel SEO-Friendly:** Struktur artikel disesuaikan agar optimal di mesin pencari.
* ⚡ **Hemat Waktu & Biaya:** Lebih cepat dan hemat hingga 80% dibanding metode konvensional.

---

Kunjungi sekarang 👉 [**Dikontenin.com**](https://dikontenin.com) dan mulai buat konten berkualitas dalam waktu singkat!


## Update Fitur

- **Antarmuka Berbasis Web**: Dashboard yang intuitif untuk mengelola sumber
- **Crawling yang Powerful**: Ekstraksi konten menggunakan Selenium WebDriver
- **Ekstraksi Konten**: Membersihkan dan mengekstrak konten utama dari halaman web
- **Caching Pintar**: Caching yang dapat dikonfigurasi untuk menghindari crawling ulang
- **Pencarian & Penyaringan**: Cepat menemukan sumber yang sudah di-crawl berdasarkan URL atau judul
- **Operasi Massal**: Pilih dan salin beberapa sumber sekaligus
- **API RESTful**: Akses terprogram ke semua fungsionalitas
- **Desain Responsif**: Berfungsi pada perangkat desktop dan tablet

## Persyaratan

- Python 3.12+
- Browser Chrome atau Firefox
- Paket Python yang diperlukan (lihat requirements.txt)
- Google Chrome (untuk Selenium WebDriver)

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

## Penggunaan

Ini akan:
1. Memulai server FastAPI
2. Membuka antarmuka web di browser default Anda
3. Menampilkan status server di GUI

Antarmuka web memungkinkan Anda untuk:

1. **Crawl URL Baru**
   - Masukkan URL di bidang input
   - Klik "Crawl" untuk memulai proses crawling
   - Lihat status dan hasil di antarmuka

2. **Pencarian dan Penyaringan**
   - Cari halaman yang di-crawl berdasarkan URL atau judul
   - Filter hasil berdasarkan rentang tanggal
   - Urutkan hasil berdasarkan kolom yang berbeda

3. **Lihat Konten**
   - Klik pada hasil apa pun untuk melihat konten lengkap yang diekstrak
   - Perluas/ciutkan bagian konten
   - Salin konten ke clipboard dalam format JSON

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

## Menjalankan Secara Lokal

1. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```

2. Mulai aplikasi:
   ```bash
   python main_gui.py
   ```

3. Akses antarmuka web di: http://localhost:8000

## Lisensi

Lisensi MIT

## Dukungan

Untuk dukungan, silakan buka issue di repository.