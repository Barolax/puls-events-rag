"""
Interface Streamlit - Puls-Events Chatbot
"""
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration de la page
st.set_page_config(
    page_title="Puls-Events Chatbot",
    page_icon="🎭",
    layout="centered"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #FF4B4B;
        font-size: 2.5em;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 2em;
    }
    </style>
""", unsafe_allow_html=True)

# Titre
st.markdown('<p class="main-title">🎭 Puls-Events Chatbot</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Découvrez les événements culturels de Lille !</p>', unsafe_allow_html=True)

# Initialiser le chatbot une seule fois
@st.cache_resource
def load_chatbot():
    from src.rag_chain import load_vector_store_langchain, create_rag_chain
    vector_store = load_vector_store_langchain()
    rag_chain, memory = create_rag_chain(vector_store)
    return rag_chain, memory

with st.spinner("🚀 Chargement du chatbot..."):
    rag_chain, memory = load_chatbot()

st.success("✅ Chatbot prêt !")

# Initialiser l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Bonjour ! 👋 Je suis votre assistant événements culturels de Lille. Que recherchez-vous ? Des concerts, des expositions, du théâtre ?"
    })

# Afficher l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utilisateur
if user_input := st.chat_input("Posez votre question sur les événements de Lille..."):

    # Afficher le message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Générer la réponse directement avec rag_chain
    with st.chat_message("assistant"):
        with st.spinner("🔍 Recherche en cours..."):
            response = rag_chain.invoke({"question": user_input})
            answer = response["answer"]
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# Sidebar
with st.sidebar:
    st.title("ℹ️ Informations")
    st.markdown("""
    **Puls-Events Chatbot** utilise :
    - 🧠 **Mistral AI** pour comprendre vos questions
    - 🔍 **Faiss** pour rechercher les événements
    - 🔗 **LangChain** pour orchestrer le tout
    """)

    st.divider()

    st.markdown("**📊 Base de données**")
    st.markdown("- 545 événements de Lille")
    st.markdown("- Période : Feb 2026 - Feb 2027")

    st.divider()

    if st.button("🔄 Nouvelle conversation"):
        st.session_state.messages = []
        memory.clear()
        st.rerun()

    st.divider()

    st.markdown("**💡 Exemples de questions**")
    st.markdown("- Quels concerts ce weekend ?")
    st.markdown("- Y a-t-il des expositions gratuites ?")
    st.markdown("- Du théâtre pour enfants ?")