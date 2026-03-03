# 📘 Manual Kolaborasi Development Odoo dengan Git

## 📌 Jawaban Singkat

**Ya, development Odoo (termasuk ERPNext) bisa dan SANGAT DIREKOMENDASIKAN menggunakan Git.**

Odoo sendiri di-develop menggunakan Git (repository resmi ada di [github.com/odoo/odoo](https://github.com/odoo/odoo)). Untuk custom module yang kita buat, kita juga menggunakan Git untuk:
- Version control (lacak perubahan kode)
- Kolaborasi tim (banyak developer kerja bareng)
- Deployment (deploy ke server produksi)
- Backup kode

---

## 🏗️ Struktur Project Odoo dengan Git

```
Server Odoo
├── /opt/odoo/odoo-bin          ← Core Odoo (JANGAN diedit)
├── /opt/odoo/addons/           ← Modul bawaan Odoo (JANGAN diedit)
│
└── /home/edi/custom_addons/    ← 🎯 CUSTOM ADDONS → INI YANG DI-GIT
    ├── produksi_edi/           ← Modul produksi kita
    ├── modul_lain/             ← Modul custom lain (kalau ada)
    └── .git/                   ← Git repository
```

**Yang di-track Git** = hanya folder `custom_addons` (modul buatan kita sendiri).
**Yang TIDAK di-Git** = Core Odoo, karena itu diinstall via package manager.

---

## 🚀 LANGKAH 1: Setup Repository Git

### 1.1 Inisialisasi Git di folder custom_addons

```bash
cd /home/edi/custom_addons

# Inisialisasi git
git init

# Buat .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.pyc
*.pyo

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Odoo
*.log
filestore/
sessions/
EOF

# Initial commit
git add .
git commit -m "Initial commit: Modul Produksi Susu Kedelai v2.0"
```

### 1.2 Push ke Remote Repository (GitHub/GitLab)

```bash
# Buat repository di GitHub/GitLab dulu, lalu:
git remote add origin https://github.com/USERNAME/odoo-custom-addons.git
git branch -M main
git push -u origin main
```

**Platform Git yang bisa dipakai:**

| Platform | Kelebihan | Harga |
|----------|-----------|-------|
| **GitHub** | Paling populer, CI/CD bagus | Gratis (public/private repo) |
| **GitLab** | Self-hosted option, CI/CD built-in | Gratis (unlimited private repo) |
| **Bitbucket** | Integrasi Jira/Atlassian | Gratis (sampai 5 user) |
| **Gitea** | Self-hosted, ringan | Gratis (open source) |

> 💡 **Rekomendasi**: Pakai **GitHub** (paling mudah) atau **GitLab** (kalau mau self-hosted).

---

## 👥 LANGKAH 2: Workflow Kolaborasi Tim

### 2.1 Branching Strategy (Git Flow Sederhana)

```
main (production)
 │
 ├── develop (staging/testing)
 │    │
 │    ├── feature/template-produksi    ← Developer A
 │    ├── feature/laporan-produksi     ← Developer B
 │    ├── fix/bug-progress-bar         ← Developer A
 │    └── feature/dashboard            ← Developer C
 │
 └── hotfix/urgent-fix                 ← Perbaikan darurat
```

**Penjelasan:**

| Branch | Fungsi | Siapa yang push |
|--------|--------|----------------|
| `main` | Kode yang sudah di server produksi. **JANGAN push langsung!** | Hanya via merge dari `develop` |
| `develop` | Kode yang sedang di-test di server staging | Merge dari feature branches |
| `feature/*` | Fitur baru yang sedang dikerjakan | Masing-masing developer |
| `fix/*` | Perbaikan bug | Developer yang fix |
| `hotfix/*` | Perbaikan darurat di production | Senior developer |

### 2.2 Alur Kerja Developer

```
1. Developer ambil tugas
   └── git checkout develop
   └── git pull origin develop
   └── git checkout -b feature/nama-fitur

2. Developer coding
   └── (edit file, test lokal)
   └── git add .
   └── git commit -m "feat: tambah fitur laporan produksi"

3. Developer push
   └── git push origin feature/nama-fitur

4. Developer buat Pull Request / Merge Request
   └── Di GitHub/GitLab, buat PR dari feature/nama-fitur → develop
   └── Minta review dari developer lain

5. Review & Merge
   └── Reviewer cek kode
   └── Kalau OK, merge ke develop
   └── Test di server staging

6. Deploy ke Production
   └── Merge develop → main
   └── Deploy ke server production
```

### 2.3 Contoh Perintah Sehari-hari

```bash
# ===== MULAI KERJA =====

# Pindah ke branch develop, ambil update terbaru
git checkout develop
git pull origin develop

# Buat branch fitur baru
git checkout -b feature/laporan-harian

# ===== SELAMA CODING =====

# Cek status perubahan
git status

# Lihat perubahan yang dibuat
git diff

# Simpan perubahan (commit)
git add .
git commit -m "feat: tambah laporan harian produksi"

# Bisa commit berkali-kali selama development
git add .
git commit -m "fix: perbaiki format tanggal di laporan"

# ===== SELESAI CODING =====

# Push ke remote
git push origin feature/laporan-harian

# Buat Pull Request di GitHub/GitLab (via browser)
# Minta review dari rekan kerja

# ===== SETELAH DI-MERGE =====

# Pindah ke develop, ambil update
git checkout develop
git pull origin develop

# Hapus branch fitur yang sudah selesai
git branch -d feature/laporan-harian
```

### 2.4 Konvensi Pesan Commit

```bash
# Format: <tipe>: <deskripsi singkat>

feat: tambah template produksi susu kedelai
fix: perbaiki progress bar tidak update
refactor: perbaiki struktur model produksi
docs: tambah panduan penggunaan
style: rapikan format kode
test: tambah unit test untuk order produksi
```

---

## 🔧 LANGKAH 3: Setup Multi-Developer

### 3.1 Tambah Collaborator di GitHub

1. Buka repository di GitHub
2. **Settings** → **Collaborators** → **Add people**
3. Masukkan username GitHub rekan developer
4. Mereka akan dapat invitation via email

### 3.2 Clone Repository (untuk developer baru)

```bash
# Developer baru clone repository
cd /home/developer-baru/
git clone https://github.com/USERNAME/odoo-custom-addons.git custom_addons

# Setup Odoo config untuk pakai custom_addons ini
# Edit /etc/odoo/odoo.conf:
# addons_path = /opt/odoo/addons,/home/developer-baru/custom_addons
```

### 3.3 Resolusi Konflik

Kalau 2 developer edit file yang sama:

```bash
# Sebelum push, selalu pull dulu
git pull origin develop

# Kalau ada konflik:
# 1. Git akan kasih tahu file mana yang konflik
# 2. Buka file tersebut, cari tanda <<<<<<<
# 3. Pilih kode yang benar, hapus tanda konflik
# 4. Commit resolusi:
git add .
git commit -m "merge: resolve conflict di produksi_order.py"
git push origin feature/nama-fitur
```

---

## 📂 Best Practices Odoo + Git

### ✅ DO (Lakukan)
- Commit sering dengan pesan yang jelas
- Selalu buat branch baru untuk setiap fitur/fix
- Test di lokal sebelum push
- Review kode sebelum merge ke develop
- Backup database secara terpisah (Git hanya untuk KODE, bukan database)

### ❌ DON'T (Jangan)
- Jangan push langsung ke `main`
- Jangan commit file database (.sql, .dump)
- Jangan commit file `__pycache__/`
- Jangan commit file konfigurasi yang berisi password (`odoo.conf`)
- Jangan edit core Odoo, selalu buat custom module
