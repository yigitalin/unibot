# UniBot - Yerel LLM Destekli Doküman Soru-Cevap Servisi

## Projenin Kısa Açıklaması
UniBot, kullanıcıların kendi yükledikleri PDF dokümanları üzerinden soru sorabilmesini sağlayan, tamamen yerelde (local) çalışan bir RAG (Retrieval-Augmented Generation) servisidir. Bu proje "1. Hafta - Orta Seviye Case Study" isterlerine uygun olarak geliştirilmiştir.

Sistem, yüklenen belgeleri parçalara ayırarak bir vektör veritabanında indeksler. Kullanıcı bir soru sorduğunda, sadece bu belgelerdeki ilgili bağlamı bularak yerel bir Büyük Dil Modeli (LLM) aracılığıyla anlamlı bir Türkçe cevap üretir. Sistemde cevap bulunamazsa, halüsinasyon (uydurma) yapmak yerine kullanıcıyı resmi kaynaklara (örneğin üniversitenin resmi web sitesine) yönlendirecek güvenli bir fallback (geri çekilme) mekanizması kurgulanmıştır.

---

# Kullanılan Ana Teknolojiler ve Tercih Nedenleri

Proje, verilerin hiçbir şekilde bulut ortamına veya üçüncü parti sunuculara gönderilmemesi prensibiyle, tamamen lokalde çalışacak şekilde tasarlanmıştır.

### LLM ve Model Yönetimi (Ollama & `gemma3:4b`)
Yerel LLM sunucusu olarak **Ollama** tercih edilmiştir. Ollama'nın kurulumu, API sunması ve donanım kaynaklarını optimize etmesi oldukça pratiktir. Model olarak Google'ın açık kaynaklı **`gemma3:4b`** modeli seçilmiştir; çünkü kişisel bilgisayarlarda (RAM/VRAM kısıtlamaları altında) hızlı çalışırken aynı zamanda Türkçe bağlamı anlama konusunda oldukça başarılı bir denge sunar.

### Embedding Modeli (`nomic-embed-text`)
Metinleri vektörlere dönüştürmek için LLM'den bağımsız, sadece bu iş için optimize edilmiş hafif ve performanslı **`nomic-embed-text`** kullanılmıştır.

### Vektör Veritabanı (FAISS)
Doküman parçaları (chunk) arasında hızlı anlamsal (semantic) arama yapabilmek için Facebook'un geliştirdiği **FAISS (Facebook AI Similarity Search)** kullanılmıştır. Bellek (RAM) üzerinde son derece verimli ve düşük gecikmeli çalıştığı için bu çaptaki bir proje için ideal bir seçimdir.

### Orkestrasyon (LangChain)
PDF yükleme (`PyPDFLoader`), metin parçalama (`RecursiveCharacterTextSplitter`) ve RAG zincirini kurma işlemleri için standartlaşmış bir yapı sunan **LangChain** kullanılmıştır.

### Backend API (FastAPI & Pydantic)
Servis katmanı **FastAPI** ile geliştirilmiştir. Hızlı olması, asenkron yapıyı desteklemesi ve **Pydantic** ile gelen verileri otomatik doğrulaması sebebiyle tercih edilmiştir. İsterlere uygun olarak `/health`, `/chat` ve `/knowledge-bases` endpoint'leri sunar.

### Kullanıcı Arayüzü (Streamlit)
Backend API'nin yeteneklerini görselleştirmek ve uçtan uca akışı sergilemek için hızlı prototipleme imkanı sunan **Streamlit** ile minimal bir arayüz geliştirilmiştir.

---

# Kurulum ve Çalıştırma Adımları

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla izleyebilirsiniz.

## 1. Ön Koşullar

- Python 3.10+
- Ollama (Yerel model çalıştırıcısı)

---

## 2. Ollama Modellerini İndirme

Sistemin çalışması için öncelikle Ollama'nın arka planda çalışıyor olması ve ilgili modellerin indirilmiş olması gerekir.

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

---

# 3. Proje Kurulumu

Proje dizininde bir sanal ortam (virtual environment) oluşturun ve aktif edin.

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

---

# 4. Servisleri Başlatma

Proje iki ayrı servisten oluşmaktadır. İki ayrı terminal açarak (ikisinde de sanal ortamın aktif olduğundan emin olun) aşağıdaki komutları çalıştırın.

## Terminal 1 – FastAPI Backend Servisi

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

API şu adreste çalışacaktır:

```
http://127.0.0.1:8000
```

Servisin çalıştığını kontrol etmek için:

```
http://127.0.0.1:8000/health
```

---

## Terminal 2 – Streamlit Arayüzü

```bash
python -m streamlit run ui.py --server.headless true --server.address 127.0.0.1 --server.port 8501
```

---

# 5. Kullanım

Tarayıcınızdan aşağıdaki adrese giderek arayüze erişebilirsiniz:

```
http://127.0.0.1:8501
```

Kullanım adımları:

1. Yan panelden **PDF yükleyin**
2. Dokümanların **indekslenmesini bekleyin**
3. Ana ekrandan **belgelerle ilgili sorular sorun**

UniBot, sorularınıza sadece yüklediğiniz dokümanlara dayanarak cevap verecektir.