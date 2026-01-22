# 🚀 VS Code'da Projeyi Çalıştırma Rehberi

## 📋 Gereksinimler

1. **Docker Desktop** yüklü ve çalışıyor olmalı
2. **VS Code** yüklü olmalı
3. **Docker Extension** (opsiyonel ama önerilir)

## 🎯 Hızlı Başlangıç

### Yöntem 1: Terminal'den (Önerilen)

VS Code'da terminal açın (`Ctrl + ~` veya `Terminal > New Terminal`) ve şu komutları çalıştırın:

```bash
# 1. Proje dizinine gidin (eğer değilseniz)
cd citegraph

# 2. Tüm servisleri başlatın
docker-compose up --build -d

# 3. Servislerin durumunu kontrol edin
docker-compose ps

# 4. API loglarını izleyin (opsiyonel)
docker-compose logs -f api
```

### Yöntem 2: VS Code Tasks Kullanarak

1. `Ctrl + Shift + P` (veya `Cmd + Shift + P` Mac'te)
2. "Tasks: Run Task" yazın
3. Şu task'lardan birini seçin:
   - **Docker: Start All Services** - Servisleri başlatır
   - **Docker: Rebuild and Start** - Yeniden build edip başlatır
   - **Docker: Stop All Services** - Servisleri durdurur
   - **Docker: View Logs** - Logları gösterir

## 📝 Detaylı Komutlar

### Servisleri Başlatma

```bash
# Normal başlatma
docker-compose up -d

# Yeniden build ile başlatma (kod değişikliklerinden sonra)
docker-compose up --build -d

# Foreground'da çalıştırma (logları görmek için)
docker-compose up
```

### Servisleri Durdurma

```bash
# Servisleri durdur (container'ları kaldır)
docker-compose down

# Servisleri durdur + volume'ları sil (veritabanı verilerini siler)
docker-compose down -v
```

### Logları İzleme

```bash
# Tüm servislerin logları
docker-compose logs -f

# Sadece API logları
docker-compose logs -f api

# Son 50 satır
docker-compose logs --tail=50 api
```

### Servis Durumunu Kontrol

```bash
# Çalışan servisleri listele
docker-compose ps

# Detaylı bilgi
docker-compose ps -a
```

### Container'a Bağlanma

```bash
# API container'ına bağlan
docker-compose exec api bash

# PostgreSQL'e bağlan
docker-compose exec db psql -U postgres -d citegraph

# Redis'e bağlan
docker-compose exec redis redis-cli
```

## 🔧 VS Code Extension'ları (Önerilen)

1. **Docker** - Microsoft
   - Container'ları yönetmek için

2. **Python** - Microsoft
   - Python kodlarını düzenlemek için

3. **Remote - Containers** - Microsoft
   - Container içinde geliştirme yapmak için (opsiyonel)

## 🌐 Erişim

Servisler başladıktan sonra:

- **Web Arayüzü**: http://localhost:8000
- **API Dokümantasyonu**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 🐛 Sorun Giderme

### Port zaten kullanılıyor hatası

```bash
# Port 8000'i kullanan process'i bul
netstat -ano | findstr :8000

# Windows'ta process'i sonlandır
taskkill /PID <process_id> /F
```

### Container başlamıyor

```bash
# Logları kontrol et
docker-compose logs api

# Container'ı yeniden oluştur
docker-compose up --build --force-recreate -d
```

### Veritabanı bağlantı hatası

```bash
# Veritabanı container'ının çalıştığından emin ol
docker-compose ps db

# Veritabanını yeniden başlat
docker-compose restart db
```

## 📦 Yeni Bağımlılık Eklendiğinde

```bash
# requirements.txt'e yeni paket eklendi
# Container'ı yeniden build et
docker-compose up --build -d
```

## 🎯 Geliştirme İçin İpuçları

1. **Hot Reload**: Backend kodunda değişiklik yaptığınızda container'ı yeniden başlatmanız gerekir
   ```bash
   docker-compose restart api
   ```

2. **Frontend Değişiklikleri**: Static dosyalar volume ile mount edildiği için değişiklikler anında yansır (sayfayı yenileyin)

3. **Veritabanı Reset**: Verileri sıfırlamak için
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

## 📚 Daha Fazla Bilgi

- Docker Compose dokümantasyonu: https://docs.docker.com/compose/
- FastAPI dokümantasyonu: https://fastapi.tiangolo.com/

