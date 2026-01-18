# Real-Time Analytics Fabric

YOLO11 nesne tespit modeli ile videolardan gerçek zamanlı insan tespiti yapan ve Microsoft Fabric ekosistemi üzerinde analiz eden bir projedir.

## Proje Özeti

Bu çözüm, video veya webcam görüntülerinden insan tespiti yapar, tespit edilen her benzersiz kişiyi Azure Event Hub üzerinden Microsoft Fabric'e gönderir ve Power BI ile gerçek zamanlı görselleştirir.

## Mimari

Proje 5 ana bileşenden oluşur: 

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. Video İşleme (Python)                                  │
│     └─ YOLO11 + BoTSORT                                    │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │ JSON veri akışı
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  2. Veri Toplama (Azure Event Hub)                         │
│     └─ Gerçek zamanlı mesaj kuyruğu                        │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  3. Veri Akışı (Fabric Event Stream)                       │
│     └─ Kaynaktan hedefe veri yönlendirme                   │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  4. Veri Depolama (Eventhouse/KQL Database)                │
│     └─ Yüksek performanslı zaman serisi veritabanı         │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  5. Görselleştirme (Power BI)                              │
│     └─ Gerçek zamanlı dashboard ve raporlama               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Bileşen Açıklamaları

**1. Video İşleme Katmanı (Python)**
- YOLO11 modeli ile nesne tespiti
- BoTSORT algoritması ile takip
- Her benzersiz kişi için JSON payload üretimi

**2. Veri Toplama Katmanı (Azure Event Hub)**
- Yüksek hacimli veri alımı
- Mesaj buffering ve yönetimi
- Partition bazlı paralel işleme

**3. Veri Akışı Katmanı (Fabric Event Stream)**
- Event Hub'dan veri okuma
- Transformasyon (opsiyonel)
- Eventhouse'a yazma

**4. Veri Depolama Katmanı (Eventhouse)**
- KQL Database ile yüksek performanslı sorgulama
- Zaman serisi optimizasyonu
- Otomatik indexleme

**5. Görselleştirme Katmanı (Power BI)**
- DirectQuery ile gerçek zamanlı bağlantı
- İnteraktif dashboard'lar
- Otomatik yenileme

## Kurulum

### Gereksinimler

- Python 3.8+
- Azure subscription
- Microsoft Fabric lisansı (Trial yeterli)
- Power BI Desktop

### Adım 1: Python Ortamı

```bash
git clone https://github.com/grivasn/real_time_analytics_fabric.git
cd real_time_analytics_fabric
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Adım 2: Azure Event Hub

1. Azure Portal'da Event Hub Namespace oluşturun
2. Namespace içinde Event Hub instance oluşturun
3. Connection string'i kopyalayın
4. Proje dizininde `.env` dosyası oluşturup connection string'i ekleyin

```env
CONN_URL=Endpoint=sb://your-namespace.servicebus.windows.net/;SharedAccessKeyName=... ;SharedAccessKey=...;EntityPath=...
```

### Adım 3: Microsoft Fabric Workspace

1. Fabric portal'da yeni workspace oluşturun
2. Event Stream oluşturup Azure Event Hub'a bağlayın
3. Eventhouse ve KQL Database oluşturun
4. KQL'de tabloyu oluşturun: 
5. Event Stream'den Eventhouse'a destination ekleyin

### Adım 4: Python Uygulamasını Çalıştırma

```bash
python meetup.py
```

### Adım 5: Power BI Dashboard

1. Power BI Desktop'ta Azure Data Explorer (Kusto) connector ile bağlanın
2. `live_p` tablosunu yükleyin
3. Görseller oluşturun ve otomatik yenileme ayarlayın

## Veri Akışı

Python uygulaması şu formatta JSON gönderir:

```json
{
  "ID": 1,
  "Confidence": 0.87,
  "Timestamp": "2026-01-18T15:30:45.123456",
  "source": "video.mp4",
  "Time": "2026-01-18 15:30"
}
```

## KQL Sorgu Örnekleri

### Temel İstatistikler

```kql
// Toplam benzersiz kişi
live_p
| summarize Toplam_Kisi = dcount(ID)

// Ortalama güven skoru
live_p
| summarize Ortalama_Confidence = round(avg(Confidence), 2)

// Toplam tespit sayısı
live_p
| count
```

### Zamansal Analizler

```kql
// Dakikalık trend (Line Chart)
live_p
| extend Time_dt = todatetime(Time)
| summarize adet = count(ID) by Time_dt
| order by Time_dt asc
| render linechart

// Saatlik dağılım
live_p
| extend Time_dt = todatetime(Time)
| summarize adet = count(ID) by bin(Time_dt, 1h)
| order by Time_dt asc
| render timechart
```

### Kaynak Analizleri

```kql
// Kaynak bazlı tespit sayıları (Bar Chart)
live_p
| summarize adet = count() by source
| top 10 by adet desc
| render barchart

// Kaynak ve zaman bazlı analiz
live_p
| extend Time_dt = todatetime(Time)
| summarize adet = count(ID) by bin(Time_dt, 1m), source
| order by Time_dt asc
```

### Güven Skoru Analizleri

```kql
// Ortalama güven skoru kartı
live_p
| summarize Ortalama_Confidence = round(avg(Confidence), 2)
| render card

// Güven skoru dağılımı
live_p
| summarize adet = count() by bin(Confidence, 0.1)
| render columnchart

// Yüksek güvenli tespitler
live_p
| where Confidence >= 0.8
| summarize adet = count()
```

## Power BI Dashboard Önerileri

**Önerilen Görseller:**
- **Card**:  Toplam benzersiz kişi sayısı
- **Card**: Ortalama güven skoru
- **Line Chart**: Zamansal trend (dakikalık)
- **Bar Chart**: Kaynak bazlı dağılım
- **Stacked Column Chart**: Kaynak ve zaman bazlı
- **Table**: Son tespitler listesi

**Otomatik Yenileme:**
- File → Options → Data Load → Automatic page refresh → 5 saniye

## Kullanım Senaryoları

- **Perakende**:  Mağaza içi müşteri sayımı ve yoğunluk analizi
- **Güvenlik**: Kamera görüntülerinden kişi takibi
- **Etkinlik Yönetimi**: Katılımcı sayısı ve akış analizi
- **Akıllı Bina**: Bina içi doluluk takibi

## Özelleştirme

### Farklı Video Kaynağı

```python
# Webcam
results = model.track(source=0, ...)

# Farklı video dosyası
results = model.track(source="baska_video.mp4", ...)

# RTSP stream
results = model.track(source="rtsp://camera_ip: 554/stream", ...)
```

### Güven Skoru Ayarlama

```python
conf=0.5  # %50 (varsayılan)
conf=0.7  # Daha az yanlış pozitif
conf=0.3  # Daha fazla tespit
```

### Farklı Nesne Tespiti

```python
classes=0        # Sadece insan
classes=[0,1]    # İnsan ve bisiklet
classes=None     # Tüm nesneler (80 sınıf)
```

## Teknik Detaylar

**YOLO Modelleri:**
- `yolo11n.pt`: Nano model (5.6MB, hızlı)
- `yolo11s.pt`: Small model (19MB, daha iyi doğruluk)

**Tracker Algoritması:**
- BoTSORT: Uzun süreli takip için optimize edilmiş

**Veri Gönderim:**
- Batch processing ile verimli transfer
- Sadece yeni tespit edilen ID'ler gönderilir

## Sorun Giderme

**Veri gelmiyor:**
```kql
// KQL'de kontrol
live_p | count
```

**Bağlantı hatası:**
- `.env` dosyasını ve connection string'i kontrol edin

**Düşük performans:**
- Daha hafif model kullanın (`yolo11n.pt`)
- `show=False` yaparak görüntülemeyi kapatın

## Kaynaklar

- [YOLO11 Dokümantasyonu](https://docs.ultralytics.com/)
- [Azure Event Hub](https://learn.microsoft.com/azure/event-hubs/)
- [Microsoft Fabric](https://learn.microsoft.com/fabric/)
- [KQL Referansı](https://learn.microsoft.com/azure/data-explorer/kusto/query/)

## Lisans

MIT License

## İletişim

GitHub Issues üzerinden soru ve önerilerinizi paylaşabilirsiniz. 

---

**Not**: Bu proje eğitim ve demo amaçlıdır. 
