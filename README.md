**Yerel RAG (Retrieval-Augmented Generation) API Motoru**

**Projenin Kısa Açıklaması**

Bu proje, veri gizliliğini (data privacy) korumak amacıyla tamamen yerel donanım üzerinde çalışan, dışarıya kapalı bir RAG arama motorudur. Sistem, İstanbul Okan Üniversitesi öğrenci süreçlerine ait (Staj, Erasmus, Burs vb.) PDF dokümanlarını okuyup vektör uzayında indeksler ve kullanıcının sorularını sadece bu belgeler bağlamında yanıtlar.

Veri akışı modern bir REST API (FastAPI) mimarisi ile karşılanarak, büyük dil modelinin (LLM) bilgi uydurması (halüsinasyon) kesin olarak engellenir.

---

**Kullanılan Ana Teknolojiler ve Tercih Nedenleri**

Sistemi tasarlarken performans, güvenlik ve **Görevlerin Ayrılığı (Separation of Concerns)** prensiplerine göre aşağıdaki teknolojiler seçilmiştir.

**Ollama & Llama3 (LLM)**  
Bulut API'lerini kullanmak kurumsal verilerin dışarı çıkması riskini taşıdığı için yerel inference çözümü tercih edilmiştir. Hafif yapısı ve yüksek performansı nedeniyle Llama3 modeli sisteme entegre edilmiştir.

**LangChain**  
Projeyi modüler ve geliştirilebilir bir orkestrasyona oturtmak için kullanılmıştır. Veri parçalama (chunking) ve LLM zincirleme işlemlerinin yönetimini sağlamaktadır.

**ChromaDB / FAISS (Vektör Veritabanı)**  
Yüksek hız gereksinimi nedeniyle doküman benzerliği aramalarını milisaniyeler içinde gerçekleştiren vektör veritabanı teknolojisi kullanılmıştır.

**FastAPI & Pydantic**  
RAG motorunu dış dünyanın kullanımına açmak için tercih edilmiştir. Doğuştan asenkron desteği performansı artırırken, Pydantic sayesinde veri doğrulama işlemleri API katmanında hata yönetimiyle birlikte sunulmuştur.

---

**Kurulum ve Çalıştırma Adımları**

Projeyi yerel bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla izleyin.

**1. Projeyi Klonlayın ve Klasöre Girin**

```bash
git clone https://github.com/yigitalin/DOCUBOT.git
cd DOCUBOT
```

**2. Gerekli Kütüphaneleri Yükleyin**

```bash
pip install -r requirements.txt
```

**3. Ollama Modellerini Hazırlayın**

Bilgisayarınızda Ollama'nın kurulu ve çalışıyor olduğundan emin olduktan sonra aşağıdaki modelleri indirin.

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

**4. Dokümanlarınızı Ekleyin**

Sistemin analiz etmesini istediğiniz PDF dosyalarını ana dizindeki ilgili klasöre yerleştirin.

---

**5. Sunucuyu Başlatın**

Backend servisinin ayağa kaldırılması:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Arayüzün (Streamlit) başlatılması:

```bash
streamlit run ui.py
```

---

**6. API Testi (Swagger UI)**

Tarayıcınız üzerinden aşağıdaki adrese giderek projeyi görsel arayüzden test edebilirsiniz:

```
http://127.0.0.1:8000/docs
```

---

**Hazir Olarak Kullanilabilir PDF'ler**

Aşağıdaki PDF'ler repo içinde ek kaynak dokümanlar olarak sunulmuştur. İsteyen GitHub üzerinden indirip kendi dokuman havuzuna ekleyerek kullanabilir:

- [okan_burs_rehberi.pdf](pdfs/okan_burs_rehberi.pdf)
- [okan_cap_yandal_rehberi.pdf](pdfs/okan_cap_yandal_rehberi.pdf)
- [okan_erasmus_rehberi.pdf](pdfs/okan_erasmus_rehberi.pdf)
- [okan_mezuniyet_rehberi.pdf](pdfs/okan_mezuniyet_rehberi.pdf)
- [okan_staj_yonergesi.pdf](pdfs/okan_staj_yonergesi.pdf)
