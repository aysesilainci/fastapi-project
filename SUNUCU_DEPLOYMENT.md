# 🚀 Sunucuya Deployment Rehberi

## 📋 Gereksinimler

- Sunucu IP: `45.76.254.122`
- Kullanıcı: `user`
- Parola: (Hocadan alınacak)
- Okul Numaranızın Son 3 Hanesi: `XXX` (Örn: 045 → Port: 8045)

---

## 📝 Adım Adım Deployment

### 1️⃣ Sunucuya Bağlanma

```bash
# Windows PowerShell veya Git Bash'te:
ssh user@45.76.254.122
```

Parolayı girdikten sonra sunucuya bağlanmış olacaksınız.

---

### 2️⃣ Proje Klasörünü Oluşturma

```bash
# www klasörüne gidin
cd /www

# Okul numaranızla klasör oluşturun (örn: 045)
mkdir 045
cd 045

# Veya direkt:
mkdir /www/045
cd /www/045
```

**Not:** `045` yerine kendi okul numaranızın son 3 hanesini yazın!

---

### 3️⃣ Proje Dosyalarını Yükleme

#### Seçenek A: Git ile (Önerilen)

```bash
# Git repository'niz varsa
git clone <repo-url> .

# Veya mevcut projeyi yüklemek için:
# Önce local bilgisayarınızda:
# scp -r citegraph/* user@45.76.254.122:/www/045/
```

#### Seçenek B: SCP ile Dosya Transferi

**Local bilgisayarınızda (Windows PowerShell):**

```powershell
# Proje klasörünü sunucuya kopyalayın
scp -r citegraph/* user@45.76.254.122:/www/045/
```

**Not:** `citegraph` klasörünün içindeki tüm dosyaları kopyalayın (docker-compose.yml, backend/, vb.)

---

### 4️⃣ Port Numarasını Ayarlama

`docker-compose.yml` dosyasını düzenleyin:

```bash
# Sunucuda nano editör ile açın
nano docker-compose.yml
```

**Değiştirilecek kısım:**

```yaml
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8045:8000"  # ← Burayı değiştirin! (8000 + okul numarası)
```

**Örnek:**
- Okul numarası son 3 hane: `045` → Port: `8045`
- Okul numarası son 3 hane: `123` → Port: `8123`

**Kaydet ve çık:** `Ctrl+X`, sonra `Y`, sonra `Enter`

---

### 5️⃣ Docker ve Docker Compose Kontrolü

```bash
# Docker yüklü mü kontrol edin
docker --version

# Docker Compose yüklü mü kontrol edin
docker-compose --version

# Eğer yüklü değilse (sunucu yöneticisine söyleyin)
```

---

### 6️⃣ Projeyi Çalıştırma

```bash
# Proje klasöründe olduğunuzdan emin olun
cd /www/045  # veya kendi klasörünüz

# Docker image'larını build edip servisleri başlatın
docker-compose up --build -d
```

**Açıklama:**
- `--build`: Docker image'larını yeniden oluşturur
- `-d`: Arka planda çalıştırır (detached mode)

---

### 7️⃣ Servislerin Durumunu Kontrol Etme

```bash
# Tüm servislerin durumunu kontrol edin
docker-compose ps

# Beklenen çıktı:
# NAME                STATUS          PORTS
# citegraph-api-1     Up              0.0.0.0:8045->8000/tcp
# citegraph-db-1      Up              5432/tcp
# citegraph-redis-1   Up              6379/tcp
```

**Eğer bir servis "Up" değilse:**

```bash
# Logları kontrol edin
docker-compose logs api
docker-compose logs db
docker-compose logs redis

# Servisleri yeniden başlatın
docker-compose restart
```

---

### 8️⃣ Uygulamanın Çalıştığını Test Etme

Tarayıcıda şu adresi açın:

```
http://45.76.254.122:8045
```

**Not:** `8045` yerine kendi port numaranızı yazın!

**Beklenen sonuç:**
- ✅ Ana sayfa açılmalı
- ✅ "Sistem Aktif" yazısı görünmeli
- ✅ API Docs: `http://45.76.254.122:8045/docs`

---

### 9️⃣ İlk Veri Oluşturma

1. Tarayıcıda `http://45.76.254.122:8045` adresine gidin
2. "Dashboard" sekmesine tıklayın
3. "Veri Oluştur" sekmesine gidin
4. "Veri Oluştur" butonuna tıklayın
5. **5-10 dakika bekleyin** (1M+ veri oluşturuluyor)

---

### 🔟 Hocaya Bildirme

Telegram grubunda şu mesajı yazın:

```
✅ Proje çalışıyor!
URL: http://45.76.254.122:8045
Okul No: 045 (veya kendi numaranız)
```

---

## 🛠️ Sorun Giderme

### Port Zaten Kullanılıyor

```bash
# Port'u kullanan process'i bulun
sudo netstat -tulpn | grep 8045

# Eğer başka bir process kullanıyorsa, port numaranızı değiştirin
# docker-compose.yml'de farklı bir port deneyin
```

### Container Başlamıyor

```bash
# Detaylı logları görün
docker-compose logs -f api

# Container'ı yeniden oluşturun
docker-compose down
docker-compose up --build -d
```

### Veritabanı Bağlantı Hatası

```bash
# Veritabanı container'ının çalıştığından emin olun
docker-compose ps db

# Veritabanını yeniden başlatın
docker-compose restart db

# Veritabanı loglarını kontrol edin
docker-compose logs db
```

### Disk Alanı Yetersiz

```bash
# Disk kullanımını kontrol edin
df -h

# Eski Docker image'larını temizleyin
docker system prune -a
```

---

## 📊 Servis Yönetimi

### Servisleri Durdurma

```bash
docker-compose stop
```

### Servisleri Başlatma

```bash
docker-compose start
```

### Servisleri Yeniden Başlatma

```bash
docker-compose restart
```

### Servisleri Tamamen Kaldırma

```bash
docker-compose down

# Verileri de silmek isterseniz:
docker-compose down -v
```

---

## 🔄 Güncelleme

Projeyi güncellemek için:

```bash
# Proje klasörüne gidin
cd /www/045

# Yeni dosyaları çekin (git kullanıyorsanız)
git pull

# Container'ları yeniden build edin
docker-compose up --build -d
```

---

## 📝 Önemli Notlar

1. **Port Numarası:** Mutlaka `8000 + okul numarası son 3 hane` formatında olmalı
2. **Klasör Adı:** `www` klasörü içinde okul numaranızla klasör oluşturun
3. **İlk Çalıştırma:** İlk veri oluşturma 5-10 dakika sürebilir
4. **Log Takibi:** Sorun yaşarsanız `docker-compose logs -f` komutunu kullanın

---

## ✅ Kontrol Listesi

- [ ] Sunucuya bağlandım
- [ ] `/www/XXX` klasörünü oluşturdum (XXX = okul numarası)
- [ ] Proje dosyalarını yükledim
- [ ] `docker-compose.yml`'de port numarasını değiştirdim
- [ ] `docker-compose up --build -d` komutunu çalıştırdım
- [ ] `docker-compose ps` ile servislerin çalıştığını kontrol ettim
- [ ] Tarayıcıda `http://45.76.254.122:XXXX` adresini açtım
- [ ] Ana sayfa açıldı
- [ ] İlk veriyi oluşturdum
- [ ] Hocaya bildirdim

---

**Başarılar! 🚀**
