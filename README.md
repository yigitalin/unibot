# UniBot

## Projenin Kisa Aciklamasi

UniBot, Istanbul Okan Universitesi ogrencileri icin gelistirilmis yerel LLM destekli bir dokuman soru-cevap uygulamasidir. Kullanici PDF belgelerini yukler, sistem bu belgeleri yerel olarak indeksler ve sorulari sadece yuklenen icerige gore yanitlar. Belgelerde cevap bulunamazsa kullaniciyi resmi okul web sitesine yonlendirir.

## Kurulum ve Calistirma

### Gereksinimler

- Python 3.13+
- Ollama
- `gemma3:4b`
- `nomic-embed-text`

### 1. Sanal ortam olusturma

```powershell
python -m venv venv
```

### 2. Sanal ortami aktif etme

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Bagimliliklari kurma

```powershell
python -m pip install -r requirements.txt
```

### 4. Ollama modellerini indirme

```powershell
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

### 5. Ollama'nin calistigini kontrol etme

```powershell
ollama list
```

### 6. Backend'i baslatma

```powershell
.\venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### 7. Arayuzu baslatma

Yeni bir terminalde:

```powershell
.\venv\Scripts\python.exe -m streamlit run ui.py --server.headless true --server.address 127.0.0.1 --server.port 8501
```

### 8. Uygulamayi acma

```text
http://127.0.0.1:8501
```

## Kullanilan Ana Teknolojiler ve Tercih Nedenleri

Sistem tasarlanirken performans, veri gizliligi ve gorevlerin ayriligi prensipleri esas alinmistir. Bu nedenle asagidaki teknolojiler tercih edilmistir:

- Ollama ve `gemma3:4b` (`LLM`)
  Bulut tabanli modeller yerine yerelde calisan bir mimari tercih edildi. Boylece universiteye ait belgeler sistem disina cikmadan islenebiliyor. Ollama hafif ve pratik bir model calistirma katmani sunarken, `gemma3:4b` yeterli kalite ve yerel calisma dengesi sagladigi icin secildi.

- LangChain
  RAG akisini moduler hale getirmek icin kullanildi. Dokuman parcalama, baglam toplama ve LLM zincirleme islemlerini daha duzenli ve genisletilebilir bir yapida kurmaya yardimci oldu.

- FAISS (`Vektor Veritabani`)
  Dokumanlar icinde hizli benzerlik aramasi yapmak icin tercih edildi. Bellek uzerinde verimli calistigi ve semantik aramada dusuk gecikme sundugu icin bu proje icin uygun bir secim oldu.

- `nomic-embed-text`
  Metinleri vektore cevirmek icin sohbet modelinden ayri, bu is icin optimize edilmis bir embedding modeli kullanildi. Bu sayede indeksleme daha hizli ve daha tutarli hale geldi.

- FastAPI ve Pydantic
  RAG motorunu REST API olarak sunmak icin kullanildi. FastAPI hafif ve hizli bir servis katmani saglarken, Pydantic gelen verileri dogrulayarak hatali isteklerin kontrollu sekilde yakalanmasina yardimci oldu.

- Streamlit
  Sistemin uctan uca calistigini gosteren sade bir arayuz sunmak icin secildi. Hizli prototipleme imkani verdigi icin backend odakli bir projede ek frontend maliyetini dusurdu.

- PyPDF
  Yuklenen PDF dosyalarindan metin cikarmak icin kullanildi. PDF tabanli calisma senaryosu icin yeterli ve pratik bir cozum sundu.
