# Dikontenin Helper

Aplikasi ini adalah aplikasi crawler yang dirancang untuk mengumpulkan sumber dari situs web yang diinginkan untuk Dikontenin.

## ✍️ Apa Itu Dikontenin?

**[Dikontenin](https://dikontenin.com)** adalah aplikasi pembuat konten berbahasa Indonesia dan Inggris yang dirancang untuk membantu Anda menyusun artikel berkualitas tinggi dalam waktu singkat. Dikontenin memfasilitasi proses kreatif dengan menyediakan kerangka dan draf awal yang bisa Anda kembangkan sesuai gaya dan kebutuhan.

---

## 🔍 Kenapa Harus Pakai Dikontenin?

1. **Buat Artikel Otomatis**  
   Hanya dengan memasukkan topik atau judul, Dikontenin menghasilkan artikel berkualitas tinggi yang terstruktur.  
2. **Optimasi Struktur & SEO**  
   Setiap artikel sudah diolah agar memenuhi kaidah SEO dan mudah dibaca pembaca.  
3. **Hemat Waktu & Biaya**  
   Proses penulisan yang biasanya membutuhkan berjam-jam kini bisa dipersingkat menjadi menit, tanpa mengurangi kualitas.  
4. **Hasil Tulisan Natural**  
   Bahasa yang dihasilkan tetap mengalir dan sesuai konteks, memudahkan Anda menambahkan sentuhan pribadi.

---

## ✒️ Dikontenin untuk Blogger dan Content Creator

- **Kendalikan Alur Kreatif**: Atasi kebuntuan ide dengan artikel siap edit.  
- **Fokus pada Gaya & Voice**: Gunakan Dikontenin untuk bagian yang repetitif, lalu poles dengan gaya unik Anda.  
- **Percepat Jadwal Terbit**: Buat atau update konten segar tanpa menunda kalender editorial.

---

## 🎯 Dikontenin untuk SEO Specialist

- **Search-Intent Alignment**: Artikel dibuat sesuai dengan pola pencarian yang dicari audiens.  
- **Struktur Heading & Subheading**: Mendukung optimasi on-page agar lebih mudah di-crawl mesin pencari.  
- **Konsistensi Keyword**: Bantu menjaga kepadatan dan distribusi kata kunci secara natural.

---

## 🏢 Dikontenin untuk Perusahaan dan Agensi Digital

- **Skalabilitas Konten**: Buat satu cluster artikel (hingga 30 artikel) tanpa repot menambah tim.  
- **Standardisasi Kualitas**: Pastikan setiap artikel memenuhi standar brand voice dan pedoman internal.

---

## 🚀 Ayo Coba Sekarang

Rasakan kemudahan membuat konten berkualitas dalam hitungan menit.  
👉 Kunjungi [**Dikontenin.com**](https://dikontenin.com) dan mulai percobaan gratis Anda hari ini!

---
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

---

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

---

## Lisensi

Dikontenin Helper berlisensi  [MIT](https://opensource.org/license/mit)

---

## Dukungan

Untuk dukungan, Anda dapat mengunjungi [Dikontenin.com](https://dikontenin.com)