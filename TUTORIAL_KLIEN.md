# 📖 Tutorial Lengkap: Modul Produksi Susu Kedelai - Odoo Custom

## 🎯 Apa yang Sudah Dibuat?

Modul ini dirancang untuk **manajemen produksi** dengan fitur utama:

✅ **Template/Resep Produksi per Produk** → Tiap produk punya resep & langkah proses sendiri  
✅ **Multi-Produk, Multi-Proses** → Susu Kedelai Original beda prosesnya dengan Cokelat, Melon, Strawberry  
✅ **Tracking Langkah per Order** → Operator bisa klik "Mulai" dan "Selesai" per langkah  
✅ **Progress Bar** → Lihat progress produksi secara visual  
✅ **Integrasi Sales Order** → Saat SO dikonfirmasi, order produksi otomatis terbuat  
✅ **Demo Data Lengkap** → 4 produk + 4 template sudah siap

---

## 🏗️ Arsitektur Modul

```
produksi_edi/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── produksi_template.py    ← Template/Resep (Master Data)
│   ├── produksi_order.py       ← Order/SPK Produksi (Transaksi)
│   └── sale_custom.py          ← Override Sale Order → auto buat SPK
├── views/
│   ├── template_view.xml       ← Views untuk Template
│   └── mrp_view.xml            ← Views untuk Order + Menu
├── data/
│   └── demo_data.xml           ← Data demo susu kedelai
└── security/
    └── ir.model.access.csv     ← Hak akses
```

### Hubungan Antar Model:

```
┌─────────────────────────┐
│   produksi.template     │ ← Master: Resep produksi per produk
│   (Template Produksi)   │
├─────────────────────────┤
│ - name                  │
│ - product_id            │──→ product.product
│ - deskripsi             │
│ - step_ids              │──→ produksi.template.step (langkah proses)
│ - bahan_ids             │──→ produksi.template.bahan (bahan baku default)
└─────────────────────────┘
            │
            │ (di-copy saat buat order)
            ▼
┌─────────────────────────┐
│   produksi.order        │ ← Transaksi: SPK per batch produksi
│   (Order Produksi/SPK)  │
├─────────────────────────┤
│ - name (SPK/26/03/0001) │
│ - template_id           │──→ produksi.template
│ - product_id            │──→ product.product (auto dari template)
│ - jumlah_target         │
│ - step_ids              │──→ produksi.order.step (bisa di-track!)
│ - bahan_ids             │──→ produksi.order.bahan
│ - state (draft→...→done)│
│ - progress (0-100%)     │
└─────────────────────────┘
```

---

## 🚀 LANGKAH 1: Install / Upgrade Modul

### Jika modul BELUM pernah diinstall:

```bash
# Restart Odoo dengan update modul
# Sesuaikan path python dan config kamu
python3 /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -u produksi_edi -d <nama_database> --stop-after-init
```

### Jika modul SUDAH terinstall (upgrade):

Karena struktur model berubah total (dari `produksi.sepatu` → model baru), 
kamu perlu **uninstall dulu, lalu install ulang**:

1. Buka Odoo → Menu **Apps**
2. Cari "Produksi Custom Edi"
3. Klik **Uninstall** (hapus modul lama)
4. Restart Odoo:
   ```bash
   sudo systemctl restart odoo
   ```
5. Kembali ke **Apps** → hapus filter "Apps" → cari "Produksi Custom Edi"
6. Klik **Install**

**ATAU** via command line (lebih cepat):
```bash
# Uninstall dulu (melalui Odoo UI), lalu:
python3 /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -i produksi_edi -d <nama_database> --stop-after-init
```

---

## 📋 LANGKAH 2: Verifikasi Instalasi

Setelah install, cek hal berikut:

### ✅ Menu Baru Muncul
Di menu utama Odoo, harus ada menu:
- **Produksi** (menu utama)
  - **Order Produksi (SPK)** → halaman transaksi
  - **Konfigurasi** → submenu
    - **Template Produksi** → master resep

### ✅ Data Demo Terisi
Buka **Produksi → Konfigurasi → Template Produksi**, harus ada 4 template:
1. Resep Susu Kedelai Original (7 langkah)
2. Resep Susu Kedelai Cokelat (8 langkah)
3. Resep Susu Kedelai Melon (8 langkah)
4. Resep Susu Kedelai Strawberry (9 langkah)

---

## 🎮 LANGKAH 3: Demo ke Klien - Skenario Lengkap

### Skenario A: "Beberapa Produk dengan Proses Berbeda"

**Ini jawaban langsung untuk pertanyaan klien:** _"di saya ada beberapa produk yang di produksi dengan isi proses yang berbeda beda.. apakah itu bisa diakomodir?"_

**Demo:**

1. Buka **Produksi → Konfigurasi → Template Produksi**
2. Tunjukkan bahwa ada 4 template berbeda
3. Buka **"Resep Susu Kedelai Original"**
   - Tunjukkan tab **"Langkah-Langkah Proses"** → 7 langkah (Sortasi → Pengemasan)
   - Tunjukkan tab **"Bahan Baku Default"** → Kedelai, Air, Gula, Botol
4. Kembali, buka **"Resep Susu Kedelai Cokelat"**
   - Tunjukkan bahwa langkahnya **beda**: ada tambahan **"Pencampuran Cokelat & Gula"**
   - Tunjukkan bahwa bahan bakunya juga **beda**: ada **"Bubuk Cokelat"**
5. Buka **"Resep Susu Kedelai Strawberry"**
   - Tunjukkan langkah unik: ada **"Persiapan Buah Strawberry"** dan **"Pencampuran Puree Strawberry"**
   - Bahan baku ada **"Strawberry Segar"**

**Poin ke klien:** 
> "Jadi setiap produk bisa punya template prosesnya sendiri, Pak/Bu. 
> Langkah-langkahnya bisa berbeda, bahan bakunya juga bisa berbeda. 
> Kalau nanti ada produk baru, tinggal buat template baru."

---

### Skenario B: "Buat Order Produksi Manual"

1. Buka **Produksi → Order Produksi (SPK)**
2. Klik **"Buat"**
3. Di field **"Template Produksi"**, pilih **"Resep Susu Kedelai Original"**
   - ✨ Otomatis! Langkah proses & bahan baku terisi dari template!
4. Isi:
   - Jumlah Target: **50**
   - Satuan: **Liter**
   - Target Selesai: (pilih tanggal)
5. Klik **Simpan**
6. Klik tombol **"Konfirmasi"** → status berubah ke "Dikonfirmasi"
7. Klik tombol **"Mulai Produksi"** → status berubah ke "Dalam Proses"
   - Langkah pertama otomatis berubah ke "Sedang Dikerjakan"
8. Di tab **"Langkah Proses Produksi"**:
   - Klik **"✅ Selesai"** pada langkah pertama
   - Otomatis langkah berikutnya jadi "Sedang Dikerjakan"!
   - Progress bar bergerak naik!
9. Lanjutkan sampai semua langkah selesai
10. Order otomatis masuk ke **"Quality Control"**
11. Klik **"Selesai / Lolos QC"** → status = Selesai ✅

**Poin ke klien:**
> "Operator tinggal klik tombol selesai per langkah, Pak/Bu.
> Progress terlihat real-time. Kalau semua langkah selesai, otomatis masuk QC."

---

### Skenario C: "Integrasi dari Sales Order"

1. Buka **Sales → Orders → Buat**
2. Pilih pelanggan (siapa saja)
3. Tambahkan produk:
   - Susu Kedelai Original → qty 100
   - Susu Kedelai Cokelat → qty 50
4. Klik **"Confirm"**
5. Buka **Produksi → Order Produksi (SPK)**
6. ✨ Otomatis ada 2 order produksi baru!
   - 1 untuk Susu Kedelai Original (100 unit, langkah proses dari template Original)
   - 1 untuk Susu Kedelai Cokelat (50 unit, langkah proses dari template Cokelat)

**Poin ke klien:**
> "Saat sales order dikonfirmasi, sistem otomatis buatkan SPK produksi.
> Prosesnya sudah otomatis terisi berdasarkan template produk masing-masing."

---

### Skenario D: "Tambah Produk & Template Baru"

Misalnya klien mau tambah produk baru: **Susu Kedelai Vanilla**

1. Buka **Produksi → Konfigurasi → Template Produksi**
2. Klik **"Buat"**
3. Isi:
   - Nama Template: **Resep Susu Kedelai Vanilla**
   - Produk: (buat/pilih produk "Susu Kedelai Vanilla")
4. Di tab **"Langkah-Langkah Proses"**, tambahkan:
   | Urutan | Nama Proses | Estimasi |
   |--------|------------|----------|
   | 1 | Sortasi & Pencucian | 1 jam |
   | 2 | Perendaman Kedelai | 8 jam |
   | 3 | Penggilingan | 1.5 jam |
   | 4 | Penyaringan | 1 jam |
   | 5 | Perebusan | 1 jam |
   | 6 | Pencampuran Vanilla Extract | 0.5 jam |
   | 7 | Pendinginan | 2 jam |
   | 8 | Pengemasan | 1.5 jam |
5. Di tab **"Bahan Baku Default"**, tambahkan bahan yang dibutuhkan
6. Simpan

Sekarang kalau buat SPK dengan template ini, langkah proses yang muncul sesuai!

---

## 💡 Fitur-Fitur Penting

| Fitur | Penjelasan |
|-------|-----------|
| 🔄 **Template Reusable** | Buat sekali, pakai berkali-kali untuk setiap batch produksi |
| 📊 **Progress Tracking** | Progress bar otomatis berdasarkan langkah yang selesai |
| ▶️ **Step Control** | Tombol Mulai / Selesai / Skip per langkah proses |
| 🔗 **Auto dari Sales** | Sales Order → SPK Produksi otomatis |
| 📝 **Catatan Operator** | Operator bisa tulis catatan per langkah |
| ⏱️ **Durasi Aktual** | Bisa input durasi aktual vs estimasi |
| 💬 **Chatter** | Log aktivitas dan diskusi di setiap SPK |
| 🔍 **Filter & Group By** | Cari dan kelompokkan SPK berdasarkan produk, status, PJ |

---

## ❓ FAQ untuk Klien

**Q: Kalau saya mau ubah proses produksi, apa SPK yang sudah jalan ikut berubah?**  
A: Tidak. Template hanya berlaku untuk SPK baru. SPK yang sudah dibuat tidak terpengaruh perubahan template.

**Q: Bisa skip langkah tertentu?**  
A: Bisa. Ada tombol "Skip" di setiap langkah.

**Q: Bagaimana kalau produk yang sama punya 2 resep berbeda?**  
A: Saat ini 1 produk → 1 template aktif. Tapi bisa dibuat beberapa template dan memilih manual saat buat SPK.

**Q: Bahan baku bisa diedit per SPK?**  
A: Bisa. Bahan baku dari template hanya sebagai default, bisa ditambah/kurangi per SPK.

---

## 🔧 Troubleshooting

### Error: "Table produksi_sepatu does not exist"
Model lama sudah dihapus. Uninstall modul lama dulu, lalu install ulang.

### Error: "Module not found"
Pastikan folder `produksi_edi` ada di path `addons` Odoo. Restart Odoo dan update daftar modul.

### Data demo tidak muncul
Pastikan file `data/demo_data.xml` terdaftar di `__manifest__.py` bagian `'data'`.
