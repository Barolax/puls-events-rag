"""
Chaîne RAG avec LangChain et mémoire conversationnelle
"""
import os
import sys
import faiss
import numpy as np
import pickle
from mistralai import Mistral
from langchain_mistralai import ChatMistralAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    MISTRAL_API_KEY,
    MISTRAL_MODEL,
    MISTRAL_EMBED_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    TOP_K_RESULTS,
    MEMORY_WINDOW_SIZE,
    VECTOR_STORE_PATH
)

def load_vector_store_langchain():
    """
    Charge l'index Faiss via LangChain
    """
    embeddings = MistralAIEmbeddings(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_EMBED_MODEL
    )

    vector_store = FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    print(f"✅ Base vectorielle chargée")
    return vector_store

def create_rag_chain(vector_store):
    """
    Crée la chaîne RAG avec mémoire conversationnelle
    """
    # Initialiser le LLM Mistral
    llm = ChatMistralAI(
        api_key=MISTRAL_API_KEY,
        model=MISTRAL_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS
    )

    # Initialiser la mémoire conversationnelle
    memory = ConversationBufferWindowMemory(
        k=MEMORY_WINDOW_SIZE,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # Prompt personnalisé
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""Tu es un assistant spécialisé dans les événements culturels de Lille.
Tu aides les utilisateurs à découvrir des événements culturels en te basant uniquement 
sur les informations disponibles dans la base de données.

Réponds toujours en français de manière friendly et utile.
Si tu ne trouves pas d'information pertinente, dis-le clairement.
Ne fabrique jamais d'informations.

Contexte des événements trouvés :
{context}

Question : {question}

Réponse :"""
    )

    # Créer le retriever
    retriever = vector_store.as_retriever(
        search_kwargs={"k": TOP_K_RESULTS}
    )

    # Créer la chaîne RAG
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt}
    )

    return rag_chain, memory