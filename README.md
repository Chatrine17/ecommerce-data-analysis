# Proyek Analisis Data: E-Commerce Public Dataset

**Nama:** Chatrine Zefania Manurung  
**ID Dicoding:** CDCC281D6X0742

---

##  Struktur Proyek

```
submission/
├── notebook.ipynb   
├── requirements.txt             
├── README.md   
├── url                 
├── data/                        ←
│   ├── orders_dataset.csv
│   ├── customers_dataset.csv
│   ├── order_items_dataset.csv
│   ├── products_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── sellers_dataset.csv
│   ├── geolocation_dataset.csv
│   └── product_category_name_translation.csv
└── dashboard/
    ├── dashboard.py             
    ├── main_data.csv            
    ├── rfm_segments.csv         
    └── geographic_data.csv      
```

> **Catatan:** File CSV di folder `dashboard/` di-generate otomatis oleh notebook pada bagian **Export Data untuk Dashboard**. Jalankan notebook terlebih dahulu sebelum menjalankan dashboard.

---

## 🔍 Pertanyaan Bisnis

1. **Bagaimana distribusi persentase segmen pelanggan berdasarkan analisis RFM** (Recency, Frequency, Monetary) pada seluruh transaksi e-commerce Brazil sepanjang tahun 2018, dan segmen mana yang memberikan kontribusi revenue tertinggi?

2. **Manakah 5 kota dengan rata-rata nilai transaksi (AOV) tertinggi** di Brazil pada tahun 2018, dan bagaimana pola distribusi geografisnya berdasarkan total revenue per kota?

---

## ⚙️ Setup & Instalasi

### 1. Clone / Download Proyek

```bash
git clone https://github.com/username/submission-analisis-data.git
cd submission-analisis-data
```

### 2. Buat Virtual Environment (Direkomendasikan)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Semua Dependency

```bash
pip install -r requirements.txt
```

---

## 🚀 Menjalankan Dashboard

Pastikan file CSV di folder `dashboard/` sudah ada (jalankan notebook dulu jika belum).

```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`.

### Fitur Dashboard

| Tab | Konten |
|-----|--------|
| 📈 Sales Overview | Tren revenue & order bulanan, distribusi status pesanan, AOV trend |
| 👥 RFM Segmentation | Distribusi segmen pelanggan, kontribusi revenue, profil RFM heatmap |
| 🗺️ Geographic Analysis | Top kota by AOV & revenue, distribusi per provinsi, bubble chart |
| 📦 Category Analysis | Top kategori by revenue & order, treemap pangsa pasar |
| 📋 Data Details | Tabel transaksi dengan search, sort, dan download CSV |

### Filter Interaktif (Sidebar)

- **📅 Periode Waktu** — Date range picker (Jan–Aug 2018)
- **📦 Kategori Produk** — Multiselect kategori produk
- **👥 Segmen Pelanggan** — Multiselect segmen RFM (Champions, Loyal, dll.)
- **🗺️ Provinsi** — Multiselect state/provinsi Brazil

---

## 📓 Menjalankan Notebook

```bash
jupyter notebook Proyek_Analisis_Data.ipynb
```

Atau buka langsung di **Google Colab** dengan upload file notebook dan folder `data/`.

### Alur Analisis Notebook

1. **Import Library** — pandas, numpy, matplotlib, seaborn
2. **Gathering Data** — Load 9 file CSV dataset
3. **Assessing Data** — Identifikasi missing values, duplikat, tipe data salah
4. **Cleaning Data** — Fix semua issue + merge dataset + filter 2018
5. **EDA** — 5 tahap eksplorasi (univariate, multivariate, temporal, kategorikal, RFM)
6. **Visualisasi** — 4 chart utama menjawab 2 pertanyaan bisnis
7. **Analisis Lanjutan** — City Tier Binning + Monthly Trend
8. **Conclusion & Recommendation** — Kesimpulan + 3 action item bisnis
9. **Export Data** — Generate CSV untuk dashboard

---

## 📦 Dataset

**Brazilian E-Commerce Public Dataset by Olist**  

| File | Deskripsi |
|------|-----------|
| `orders_dataset.csv` | Data pesanan utama (~99K baris) |
| `customers_dataset.csv` | Data pelanggan |
| `order_items_dataset.csv` | Item per pesanan |
| `products_dataset.csv` | Data produk |
| `order_payments_dataset.csv` | Data pembayaran |
| `order_reviews_dataset.csv` | Ulasan pelanggan |
| `sellers_dataset.csv` | Data penjual |
| `geolocation_dataset.csv` | Koordinat geografis per zip code |
| `product_category_name_translation.csv` | Terjemahan nama kategori |

---

## 🛠️ Library yang Digunakan

| Library | Versi | Kegunaan |
|---------|-------|----------|
| pandas | 2.2.2 | Manipulasi & analisis data |
| numpy | 1.26.4 | Komputasi numerik |
| matplotlib | 3.8.4 | Visualisasi statis (notebook) |
| seaborn | 0.13.2 | Visualisasi statistik (notebook) |
| plotly | 5.22.0 | Visualisasi interaktif (dashboard) |
| streamlit | 1.35.0 | Framework dashboard web |
