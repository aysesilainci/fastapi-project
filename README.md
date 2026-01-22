# 📚 CiteGraph - Akademik Atıf Analiz Sistemi

Modern, production-ready akademik atıf analiz sistemi. Google Scholar benzeri bir platform.

## 🎯 Proje Özellikleri

### ✅ Hocanın İsterleri (Tümü Karşılandı)

1. **✅ Konunun Özgünlüğü**
   - CiteGraph: Akademik makale atıf analiz sistemi
   - Google Scholar benzeri özgün bir konsept

2. **✅ API (FAST/REST)**
   - FastAPI REST API
   - Tüm endpoint'ler `/api/v1` altında
   - Otomatik API dokümantasyonu: `/docs`

3. **✅ Sentetik Veri + Cache İspatı**
   - `POST /api/v1/generate`: 1,000,000+ sentetik atıf kaydı oluşturur
   - `GET /api/v1/top-papers`: Redis cache kullanır (60 saniye TTL)
   - Cache durumu header'larda belirtilir (`X-Cache-Status`)
   - Web arayüzünde cache HIT/MISS net gösterilir

4. **✅ Responsive Web Arayüzü**
   - Modern, profesyonel tasarım
   - Mobil, tablet ve masaüstü uyumlu
   - Chart.js ile interaktif grafikler
   - Animasyonlar ve geçiş efektleri

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Docker ve Docker Compose
- En az 4GB RAM (1M+ veri için)

### Kurulum

```bash
# Projeyi klonlayın
git clone <repo-url>
cd citegraph

# Servisleri başlatın
docker-compose up --build -d

# Servislerin durumunu kontrol edin
docker-compose ps
```

### Erişim

- **Web Arayüzü**: http://localhost:8000
- **API Dokümantasyonu**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 📡 API Endpoint'leri

### 1. Veri Oluşturma
```http
POST /api/v1/generate
```
- 10,000 makale ve 1,000,000+ atıf kaydı oluşturur
- Batch insert kullanır (performans için)
- 5-10 dakika sürebilir

**Yanıt:**
```json
{
  "message": "Citation generation completed",
  "papers_created": 10000,
  "citations_created": 1000000
}
```

### 2. En Çok Atıf Alan Makaleler (Cache'li)
```http
GET /api/v1/top-papers?topic=AI&limit=50
```
- Redis cache kullanır (60 saniye TTL)
- Cache durumu header'da: `X-Cache-Status: HIT` veya `MISS`
- İlk sorgu: Cache MISS (veritabanından)
- İkinci sorgu (60 sn içinde): Cache HIT (Redis'ten)

**Yanıt:**
```json
[
  {
    "id": 1,
    "title": "Research Paper 1",
    "topic": "AI",
    "published_year": 2020,
    "citation_count": 1250,
    "citation_growth_rate": 2.5
  }
]
```

### 3. En Çok Atıf Alan Makaleler (Cache Yok)
```http
GET /api/v1/top-papers-db?topic=AI&limit=50
```
- Cache'i bypass eder, direkt veritabanından sorgular
- Cache testi için kullanılır

### 4. İstatistikler
```http
GET /api/v1/stats
```
- Toplam makale ve atıf sayıları
- Konu bazlı dağılım
- En çok atıf alan konular
- Yıl bazlı dağılım

### 5. Health Check
```http
GET /api/v1/health
```

### 6. Cache Temizleme
```http
DELETE /api/v1/cache/{topic}/{limit}
```

## 🎨 Web Arayüzü Özellikleri

### 3 Ana Sekme

1. **Veri Oluştur**
   - 1M+ sentetik veri oluşturma
   - Progress bar ile ilerleme takibi
   - Toast notification'lar

2. **En Çok Atıf Alan Makaleler**
   - Konu seçimi (dropdown)
   - İki ayrı buton:
     - 🔄 Veritabanından (Cache Yok) - Yavaş
     - ⚡ Cache'den (Hızlı) - Hızlı
   - Cache durumu göstergesi (HIT/MISS)
   - Responsive tablo görünümü

3. **İstatistikler**
   - İstatistik kartları (Toplam Makale, Atıf, Ortalama)
   - Chart.js grafikleri:
     - Konu dağılımı (Doughnut Chart)
     - En çok atıf alan konular (Bar Chart)
   - Detaylı tablolar

## 🏗️ Teknik Yapı

### Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **Frontend**: Vanilla JavaScript, Chart.js
- **Containerization**: Docker + Docker Compose

### Proje Yapısı
```
citegraph/
├── docker-compose.yml
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py
        ├── database.py
        ├── models.py
        ├── schemas.py
        ├── crud.py
        └── api/
            └── v1/
                └── endpoints.py
        └── static/
            ├── index.html
            ├── style.css
            └── script.js
```

## 🔍 Cache Sistemi

### Nasıl Çalışır?

1. **İlk Sorgu (Cache MISS)**
   - Kullanıcı `GET /api/v1/top-papers?topic=AI&limit=50` çağırır
   - Redis'te cache yok
   - PostgreSQL'den sorgulanır
   - Sonuç Redis'e kaydedilir (60 saniye TTL)
   - Response header: `X-Cache-Status: MISS`

2. **İkinci Sorgu (Cache HIT)**
   - 60 saniye içinde aynı sorgu yapılırsa
   - Redis'ten direkt döner
   - Çok daha hızlı (~10-50ms vs ~500-2000ms)
   - Response header: `X-Cache-Status: HIT`

### Cache Key Formatı
```
top_papers:{topic}:{limit}
Örnek: top_papers:AI:50
```

### Cache Testi
Web arayüzünde:
1. "Veritabanından" butonuna tıklayın → Cache MISS (yavaş)
2. "Cache'den" butonuna tıklayın → Cache HIT (hızlı)

## 📊 Veritabanı Şeması

### Paper (Makale)
- `id`: Primary Key
- `title`: Makale başlığı
- `topic`: Konu (AI, Machine Learning, vb.)
- `published_year`: Yayın yılı

### Citation (Atıf)
- `id`: Primary Key
- `source_paper_id`: Atıf yapan makale (FK)
- `target_paper_id`: Atıf alan makale (FK)
- `citation_date`: Atıf tarihi

## 🐳 Docker Servisleri

1. **api**: FastAPI uygulaması (Port: 8000)
2. **db**: PostgreSQL veritabanı (Port: 5433)
3. **redis**: Redis cache (Port: 6379)

## 🔧 Production Deployment

### Sunucuya Deploy

```bash
# 1. Projeyi sunucuya yükleyin
scp -r citegraph/ user@server:/path/to/

# 2. Sunucuda
cd /path/to/citegraph
docker-compose up --build -d

# 3. Logları kontrol edin
docker-compose logs -f api
```

### Environment Variables
Docker Compose'da tanımlı:
- `DATABASE_URL`: PostgreSQL bağlantı string'i
- `REDIS_HOST`: Redis host adresi
- `REDIS_PORT`: Redis port

### Port Yapılandırması
- API: `8000:8000` (değiştirilebilir)
- PostgreSQL: `5433:5432` (host port:container port)
- Redis: `6379:6379`

## 📝 Notlar

- İlk veri oluşturma işlemi 5-10 dakika sürebilir
- Cache TTL: 60 saniye
- Batch insert kullanıldığı için performans optimize edilmiştir
- Tüm endpoint'ler `/api/v1` prefix'i ile başlar

## 🎓 Değerlendirme Kriterleri

✅ **Konunun Özgünlüğü**: CiteGraph - Akademik atıf analizi  
✅ **API (FAST/REST)**: FastAPI REST API  
✅ **Sentetik Veri + Cache**: 1M+ veri + Redis cache (ispat edilebilir)  
✅ **Responsive Arayüz**: Modern, mobil uyumlu web arayüzü  

## 📞 Destek

Sorularınız için API dokümantasyonunu ziyaret edin: `/docs`

---

**Geliştirici**: [İsminiz]  
**Tarih**: 2024  
**Versiyon**: 1.0.0

