# 📘 Manual Deployment Self-Hosted Odoo (VPS / Server Sendiri)

## 📌 Overview

Panduan ini menjelaskan cara deploy Odoo di server sendiri (self-hosted).
Cocok untuk produksi/bisnis yang ingin kontrol penuh atas data dan sistem.

```
┌─────────────────────────────────────────────────────┐
│                    ARSITEKTUR                        │
│                                                     │
│   Internet                                          │
│      │                                              │
│      ▼                                              │
│   ┌──────────┐                                      │
│   │  Nginx   │  ← Reverse Proxy + SSL (HTTPS)      │
│   │ :80/:443 │                                      │
│   └────┬─────┘                                      │
│        │                                            │
│        ▼                                            │
│   ┌──────────┐     ┌──────────────┐                 │
│   │  Odoo    │────▶│  PostgreSQL  │                 │
│   │  :8069   │     │  (Database)  │                 │
│   └────┬─────┘     └──────────────┘                 │
│        │                                            │
│        ▼                                            │
│   ┌──────────────────────┐                          │
│   │   Custom Addons      │  ← dari Git repository   │
│   │   /custom_addons/    │                          │
│   └──────────────────────┘                          │
│                                                     │
│   Server: Ubuntu 22.04 / 24.04 LTS                  │
│   RAM: Minimal 2GB (rekomendasi 4GB)                │
│   Storage: Minimal 20GB                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🖥️ Pilihan Server / VPS

| Provider | Harga Mulai | Lokasi | Cocok Untuk |
|----------|-------------|--------|-------------|
| **DigitalOcean** | $6/bulan | Singapore | Startup, UKM |
| **Hetzner** | €4/bulan | Eropa | Hemat budget |
| **Contabo** | €5/bulan | Eropa/Asia | Hemat budget |
| **AWS Lightsail** | $5/bulan | Singapore | Enterprise |
| **Google Cloud** | $7/bulan | Jakarta | Enterprise |
| **IDCloudHost** | Rp 50rb/bulan | Jakarta | Lokal Indonesia |
| **Niagahoster VPS** | Rp 58rb/bulan | Jakarta | Lokal Indonesia |
| **Biznet Gio** | Rp 44rb/bulan | Jakarta | Lokal Indonesia |

> **Rekomendasi spec minimum**: 2 vCPU, 4GB RAM, 40GB SSD, Ubuntu 22.04/24.04

---

## 🚀 LANGKAH 1: Persiapan Server

### 1.1 Login ke Server

```bash
ssh root@IP_SERVER_KAMU
```

### 1.2 Update Sistem

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Buat User Khusus Odoo

```bash
# Buat user 'odoo' tanpa password (untuk security)
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo
```

### 1.4 Install Dependencies

```bash
# Install packages yang dibutuhkan Odoo
sudo apt install -y \
    git \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    wget \
    libfreetype6-dev \
    libxml2-dev \
    libzip-dev \
    libsasl2-dev \
    libldap2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    node-less \
    npm \
    curl
```

---

## 🗄️ LANGKAH 2: Install PostgreSQL (Database)

```bash
# Install PostgreSQL
sudo apt install -y postgresql

# Buat user database untuk Odoo
sudo su - postgres -c "createuser -s odoo"

# Verifikasi
sudo su - postgres -c "psql -c '\\du'" | grep odoo
# Harus muncul: odoo | Superuser, Create role, Create DB
```

---

## 📦 LANGKAH 3: Install Odoo

### Opsi A: Install dari Source (REKOMENDASI untuk development)

```bash
# Pindah ke user odoo
sudo su - odoo

# Clone Odoo (pilih versi yang sesuai, contoh: 17.0)
git clone https://github.com/odoo/odoo.git --depth 1 --branch 17.0 /opt/odoo/odoo

# Buat virtual environment
python3 -m venv /opt/odoo/odoo-venv

# Aktifkan venv dan install dependencies
source /opt/odoo/odoo-venv/bin/activate
pip install wheel
pip install -r /opt/odoo/odoo/requirements.txt
deactivate

# Buat folder custom addons
mkdir -p /opt/odoo/custom_addons

# Kembali ke root
exit
```

### Opsi B: Install dari Package (Lebih mudah, kurang fleksibel)

```bash
# Tambah repository Odoo
wget -O - https://nightly.odoo.com/odoo.key | sudo gpg --dearmor -o /usr/share/keyrings/odoo-archive-keyring.gpg
echo 'deb [signed-by=/usr/share/keyrings/odoo-archive-keyring.gpg] https://nightly.odoo.com/17.0/nightly/deb/ ./' | sudo tee /etc/apt/sources.list.d/odoo.list

sudo apt update
sudo apt install -y odoo
```

---

## ⚙️ LANGKAH 4: Konfigurasi Odoo

### 4.1 Buat File Konfigurasi

```bash
sudo nano /etc/odoo/odoo.conf
```

Isi dengan:

```ini
[options]
; Administrasi
admin_passwd = GANTI_DENGAN_PASSWORD_KUAT_123!

; Database
db_host = False
db_port = False
db_user = odoo
db_password = False
db_name = False

; Path
addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom_addons

; Server
http_port = 8069
logfile = /var/log/odoo/odoo.log
log_level = info

; Performance
workers = 2
max_cron_threads = 1
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200

; Proxy (untuk Nginx)
proxy_mode = True
```

### 4.2 Buat Folder Log

```bash
sudo mkdir -p /var/log/odoo
sudo chown odoo:odoo /var/log/odoo
```

---

## 🔄 LANGKAH 5: Setup Systemd Service

Agar Odoo jalan otomatis saat server reboot:

```bash
sudo nano /etc/systemd/system/odoo.service
```

Isi dengan:

```ini
[Unit]
Description=Odoo
Documentation=https://www.odoo.com
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo
PermissionsStartOnly=true
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo-venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf
StandardOutput=journal+console
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Aktifkan dan jalankan service
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo

# Cek status
sudo systemctl status odoo
```

---

## 🌐 LANGKAH 6: Setup Nginx (Reverse Proxy + SSL)

### 6.1 Install Nginx

```bash
sudo apt install -y nginx
```

### 6.2 Konfigurasi Nginx

```bash
sudo nano /etc/nginx/sites-available/odoo
```

Isi dengan:

```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoochat {
    server 127.0.0.1:8072;
}

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name erp.namadomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl;
    server_name erp.namadomain.com;

    # SSL (akan diisi oleh Certbot)
    ssl_certificate /etc/letsencrypt/live/erp.namadomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.namadomain.com/privkey.pem;

    # Proxy headers
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # Odoo
    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
    }

    # Odoo Chat (Live Chat / Websocket)
    location /websocket {
        proxy_redirect off;
        proxy_pass http://odoochat;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Cache static files
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }

    # Gzip compression
    gzip_types text/css text/plain text/xml application/xml application/javascript application/json;
    gzip on;

    # Upload size
    client_max_body_size 200m;
}
```

### 6.3 Aktifkan Konfigurasi

```bash
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test konfigurasi
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 6.4 Setup SSL (HTTPS) dengan Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Generate SSL certificate (GRATIS!)
sudo certbot --nginx -d erp.namadomain.com

# Auto-renew (sudah otomatis, tapi bisa test):
sudo certbot renew --dry-run
```

---

## 📥 LANGKAH 7: Deploy Custom Module dari Git

### 7.1 Clone Custom Addons ke Server

```bash
# Login sebagai user odoo
sudo su - odoo

# Clone repository custom addons
cd /opt/odoo/custom_addons
git clone https://github.com/USERNAME/odoo-custom-addons.git .

# Kembali ke root
exit

# Restart Odoo
sudo systemctl restart odoo
```

### 7.2 Install Modul via Browser

1. Buka `https://erp.namadomain.com` di browser
2. Login sebagai admin
3. Aktifkan **Developer Mode**: Settings → Activate Developer Mode
4. Buka **Apps** → **Update Apps List** (tombol di atas)
5. Cari modul **"Produksi Custom Edi"**
6. Klik **Install**

### 7.3 Update Modul Setelah Ada Perubahan Kode

```bash
# Cara 1: Via command line (REKOMENDASI)
sudo su - odoo
cd /opt/odoo/custom_addons
git pull origin main
exit

sudo systemctl restart odoo

# Kalau ada perubahan model/view, upgrade modul:
sudo su - odoo
/opt/odoo/odoo-venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -u produksi_edi -d NAMA_DATABASE --stop-after-init
exit

sudo systemctl restart odoo

# Cara 2: Via browser
# Settings → Apps → Cari modul → klik ⋮ → Upgrade
```

---

## 🔄 LANGKAH 8: Workflow Deployment (CI/CD Sederhana)

### Alur Development → Production

```
Developer Lokal          GitHub              Server Production
┌────────────┐     ┌──────────────┐     ┌──────────────────┐
│ Edit kode  │────▶│  Push code   │────▶│  git pull         │
│ Test lokal │     │  Merge PR    │     │  restart odoo     │
│ git commit │     │              │     │  upgrade modul    │
└────────────┘     └──────────────┘     └──────────────────┘
```

### Script Auto-Deploy (Opsional)

Buat script di server untuk memudahkan deploy:

```bash
sudo nano /opt/odoo/deploy.sh
```

```bash
#!/bin/bash
# Script deploy Odoo custom addons
# Jalankan: sudo bash /opt/odoo/deploy.sh [nama_modul] [nama_database]

MODULE=${1:-produksi_edi}
DATABASE=${2:-odoo_production}

echo "🔄 Pulling latest code..."
cd /opt/odoo/custom_addons
sudo -u odoo git pull origin main

echo "⬆️ Upgrading module: $MODULE..."
sudo -u odoo /opt/odoo/odoo-venv/bin/python3 /opt/odoo/odoo/odoo-bin \
    -c /etc/odoo/odoo.conf \
    -u $MODULE \
    -d $DATABASE \
    --stop-after-init

echo "🔄 Restarting Odoo..."
sudo systemctl restart odoo

echo "✅ Deploy selesai!"
echo "🌐 Cek di: https://erp.namadomain.com"
```

```bash
sudo chmod +x /opt/odoo/deploy.sh

# Cara pakai:
sudo bash /opt/odoo/deploy.sh produksi_edi nama_database
```

---

## 🛡️ LANGKAH 9: Keamanan & Backup

### 9.1 Firewall

```bash
# Setup UFW Firewall
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# JANGAN buka port 8069 ke publik! Nginx yang handle.
```

### 9.2 Backup Database Otomatis

```bash
# Buat script backup
sudo nano /opt/odoo/backup.sh
```

```bash
#!/bin/bash
# Backup database Odoo harian
BACKUP_DIR="/opt/odoo/backups"
DATABASE="odoo_production"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump $DATABASE | gzip > $BACKUP_DIR/${DATABASE}_${DATE}.sql.gz

# Backup filestore (attachment, gambar, dll)
tar -czf $BACKUP_DIR/filestore_${DATE}.tar.gz /opt/odoo/.local/share/Odoo/filestore/$DATABASE/

# Hapus backup lebih dari 30 hari
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "✅ Backup selesai: ${DATABASE}_${DATE}"
```

```bash
sudo chmod +x /opt/odoo/backup.sh

# Setup backup otomatis setiap hari jam 2 pagi
sudo crontab -e
# Tambahkan baris:
# 0 2 * * * /opt/odoo/backup.sh >> /var/log/odoo/backup.log 2>&1
```

### 9.3 Ganti Master Password

```bash
# Edit odoo.conf
sudo nano /etc/odoo/odoo.conf

# Ganti admin_passwd dengan password yang kuat
# admin_passwd = PASSWORD_SANGAT_KUAT_123!@#

sudo systemctl restart odoo
```

---

## 📊 Checklist Deployment

| # | Item | Status |
|---|------|--------|
| 1 | Server VPS sudah siap (Ubuntu 22.04/24.04) | ⬜ |
| 2 | PostgreSQL terinstall | ⬜ |
| 3 | Odoo terinstall dari source | ⬜ |
| 4 | Konfigurasi /etc/odoo/odoo.conf | ⬜ |
| 5 | Systemd service aktif | ⬜ |
| 6 | Nginx reverse proxy | ⬜ |
| 7 | SSL/HTTPS (Let's Encrypt) | ⬜ |
| 8 | Custom addons di-clone dari Git | ⬜ |
| 9 | Modul terinstall di Odoo | ⬜ |
| 10 | Firewall (UFW) aktif | ⬜ |
| 11 | Backup otomatis | ⬜ |
| 12 | Domain pointing ke IP server | ⬜ |

---

## ❓ FAQ

**Q: Berapa biaya self-host Odoo?**
A: Odoo Community Edition GRATIS. Biaya hanya untuk:
- VPS/Server: ±Rp 50-200rb/bulan
- Domain: ±Rp 100-150rb/tahun
- SSL: GRATIS (Let's Encrypt)
- Total: ±Rp 150-350rb/bulan

**Q: Odoo Community vs Enterprise?**
A: Community = gratis, fitur dasar lengkap. Enterprise = berbayar, ada fitur tambahan (studio, IoT, dll). Untuk UKM, Community sudah sangat cukup.

**Q: Apakah data aman?**
A: Data ada di server sendiri. Pastikan backup rutin, firewall aktif, dan SSL terpasang.

**Q: Berapa user yang bisa pakai?**
A: Odoo Community TIDAK ada batasan user. Kalau pakai VPS 4GB RAM, bisa handle 20-50 concurrent user.

**Q: Bagaimana kalau mau upgrade versi Odoo?**
A: Upgrade versi Odoo (misal 17 → 18) perlu migrasi database. Ini proses yang perlu hati-hati. Sebaiknya dilakukan oleh developer berpengalaman.
