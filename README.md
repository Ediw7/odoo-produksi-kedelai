# 🏭 Odoo Modul Produksi - Susu Kedelai

Custom Odoo module untuk manajemen produksi dengan sistem **Template Multi-Produk**.

Setiap produk bisa memiliki **proses produksi yang berbeda-beda** — lengkap dengan tracking langkah, progress bar, dan integrasi ke Sales Order.

## ✨ Fitur Utama

| Fitur | Keterangan |
|-------|-----------|
| 📋 **Template Produksi** | Buat "resep" proses produksi per produk. Reusable untuk setiap batch. |
| 🔄 **Multi-Produk Multi-Proses** | Setiap produk punya langkah proses berbeda-beda |
| ▶️ **Step Tracking** | Operator klik Mulai/Selesai per langkah proses |
| 📊 **Progress Bar** | Progress otomatis berdasarkan langkah yang selesai |
| 🔗 **Integrasi Sales** | Sales Order dikonfirmasi → SPK otomatis terbuat |
| 💬 **Chatter** | Log aktivitas dan diskusi di setiap SPK |

## 📦 Contoh Data (Demo)

Modul menyertakan 4 produk demo:

| Produk | Jumlah Langkah | Proses Unik |
|--------|---------------|-------------|
| Susu Kedelai Original | 7 langkah | Proses standar |
| Susu Kedelai Cokelat | 8 langkah | + Pencampuran Cokelat |
| Susu Kedelai Melon | 8 langkah | + Pencampuran Essence Melon |
| Susu Kedelai Strawberry | 9 langkah | + Persiapan Buah + Pencampuran Puree |

## 🔧 Instalasi

1. Clone repository ini ke folder `custom_addons` Odoo:
   ```bash
   cd /path/to/custom_addons
   git clone https://github.com/USERNAME/odoo-produksi-kedelai.git produksi_edi
   ```

2. Restart Odoo dan update daftar modul

3. Buka **Apps** → Cari **"Produksi Custom Edi"** → **Install**

## 📋 Dependencies

- `sale` (Sales)
- `mail` (Discuss/Chatter)
- `product` (Product)

## 🏗️ Struktur Modul

```
produksi_edi/
├── models/
│   ├── produksi_template.py   # Template/Resep Produksi
│   ├── produksi_order.py      # Order Produksi (SPK)
│   └── sale_custom.py         # Override Sale Order
├── views/
│   ├── template_view.xml      # View Template
│   └── mrp_view.xml           # View Order + Menu
├── data/
│   └── demo_data.xml          # Data demo 4 produk
├── security/
│   └── ir.model.access.csv    # Hak akses
└── docs/
    ├── MANUAL_GIT_KOLABORASI.md
    └── MANUAL_DEPLOYMENT_SELFHOST.md
```

## 📝 Lisensi

LGPL-3
