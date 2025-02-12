# Geliştirme Günlüğü

## 20 Mart 2024

### Yapılan İşlemler
1. AI Handler ve şablonlar güncellendi
   - Dilekçe şablonları detaylandırıldı
   - Hata yönetimi eklendi
   - Loglama sistemi kuruldu

2. Test altyapısı iyileştirildi
   - Mock kullanımı eklendi
   - SQLite test veritabanı yapılandırıldı
   - Fixture'lar düzenlendi

3. Güvenlik bileşenleri eklendi
   - JWT token sistemi kuruldu
   - Şifreleme altyapısı hazırlandı

### Yapılacaklar
- [ ] Kullanıcı kimlik doğrulama sistemi
- [ ] Daha fazla dilekçe şablonu
- [ ] Hata yönetimi geliştirmeleri
- [ ] Loglama sistemi iyileştirmeleri

# Legal AI API Dokümantasyonu

## Kurulum
1. Gereksinimleri yükle: `pip install -r requirements.txt`
2. PostgreSQL başlat: `docker compose up -d`
3. Sunucuyu başlat: `uvicorn app.main:app --reload`

## API Endpoints

### Auth
- POST `/api/v1/auth/register`: Yeni kullanıcı kaydı
- POST `/api/v1/auth/login`: Giriş
- POST `/api/v1/auth/premium/activate`: Premium aktivasyonu

### Dilekçeler
- POST `/api/v1/petitions/generate`: Dilekçe oluştur
- GET `/api/v1/petitions/list`: Dilekçeleri listele
- GET `/api/v1/petitions/{id}/pdf`: PDF indir

## Modeller
- GPT-4: Premium kullanıcılar
- GPT-3.5: Normal kullanıcılar 