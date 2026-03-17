import os
from typing import Iterable

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHAT_MODEL_NAME = os.getenv("OLLAMA_LLM_MODEL", "gemma3:4b")
VECTOR_MODEL_NAME = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OKAN_MAIN_SITE = "https://www.okan.edu.tr/"

chat_runtime = ChatOllama(model=CHAT_MODEL_NAME, temperature=0.1)
vector_runtime = OllamaEmbeddings(model=VECTOR_MODEL_NAME)


def collect_pages(source_files: Iterable[str]):
    gathered_pages = []

    for source_path in source_files:
        pdf_loader = PyPDFLoader(source_path)
        gathered_pages.extend(pdf_loader.load())

    return gathered_pages


def compose_brain(source_files: Iterable[str]):
    raw_pages = collect_pages(source_files)
    slicer = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=180)
    text_segments = slicer.split_documents(raw_pages)
    semantic_index = FAISS.from_documents(documents=text_segments, embedding=vector_runtime)

    return {
        "brain": semantic_index,
        "page_total": len(raw_pages),
        "segment_total": len(text_segments),
    }


def merge_context(matches) -> str:
    return "\n\n".join(match.page_content for match in matches)


def needs_official_redirect(answer_text: str) -> bool:
    lowered_answer = answer_text.casefold()
    fallback_markers = (
        "yuklenen pdf belgelerinde bu sorunun cevabi bulunamadi",
        "baglam yetmiyor",
        "baglamda yer almiyor",
        "baglamda bulunmuyor",
        "belgelerde yer almiyor",
        "belgelerde bulunmuyor",
        "emin degilim",
        "bu bilgi yok",
        "yeterli bilgi yok",
        "verilen baglam",
        "net cevap bulunamadi",
    )
    return any(marker in lowered_answer for marker in fallback_markers)


def run_lookup(semantic_index, user_prompt: str) -> str:
    context_port = semantic_index.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 18},
    )

    operating_rules = (
        "Sen UniBot'sun; Istanbul Okan Universitesi ogrencileri icin calisan belge tabanli bilgi asistanisin.\n"
        "Sana yuklenen belgeler; staj, burs, Erasmus, yandal, CAP ve mezuniyet sartlari gibi ogrenci surecleriyle ilgilidir.\n"
        "Yaniti sadece verilen baglamdan cikart.\n"
        "Baglam yetmiyorsa bunu acikca soyle ve ayrintili uydurma yapma.\n"
        "Tum cevaplarini Turkce ver.\n"
        "Gerekmedikce uzun yazma, net ol.\n"
        "Baglam yetersiz oldugunda sadece su cumleyi kullan: Yuklenen PDF belgelerinde bu sorunun cevabi bulunamadi.\n"
        "Baglam:\n{context}"
    )

    prompt_frame = ChatPromptTemplate.from_messages(
        [
            ("system", operating_rules),
            ("human", "{input}"),
        ]
    )

    lookup_flow = (
        {"context": context_port | merge_context, "input": RunnablePassthrough()}
        | prompt_frame
        | chat_runtime
        | StrOutputParser()
    )

    answer_text = lookup_flow.invoke(user_prompt)

    if needs_official_redirect(answer_text):
        return (
            "Yuklenen PDF belgelerinde bu sorunun cevabi bulunamadi.\n\n"
            "Konu hakkinda en guncel bilgilere burdan erisebilirsin:\n"
            f"{OKAN_MAIN_SITE}"
        )

    return answer_text
