"""
Logique principale du chatbot
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Variables globales
_rag_chain = None
_memory = None

def initialize_chatbot():
    """
    Initialise le chatbot (à appeler une seule fois au démarrage)
    """
    global _rag_chain, _memory

    print("🚀 Initialisation du chatbot...")

    from src.rag_chain import load_vector_store_langchain, create_rag_chain

    vector_store = load_vector_store_langchain()
    _rag_chain, _memory = create_rag_chain(vector_store)

    print("✅ Chatbot prêt !")
    return _rag_chain, _memory

def chat(user_message):
    """
    Envoie un message au chatbot et retourne la réponse
    """
    global _rag_chain

    if _rag_chain is None:
        initialize_chatbot()

    response = _rag_chain.invoke({"question": user_message})
    return response["answer"]

def reset_memory():
    """
    Réinitialise la mémoire conversationnelle
    """
    global _memory
    if _memory:
        _memory.clear()
        print("🔄 Mémoire réinitialisée")

if __name__ == "__main__":
    print("🎭 Chatbot Puls-Events - Lille")
    print("Tapez 'quit' pour quitter\n")

    initialize_chatbot()

    while True:
        user_input = input("Vous : ").strip()

        if user_input.lower() == "quit":
            print("Au revoir !")
            break

        if not user_input:
            continue

        print("Bot : ", end="", flush=True)
        response = chat(user_input)
        print(response)
        print()