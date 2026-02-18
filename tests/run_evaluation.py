"""
Script d'évaluation du chatbot avec le jeu de données test
"""
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_test_dataset():
    """Charge le jeu de données test"""
    with open("tests/test_dataset.json", "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_chatbot():
    """Teste le chatbot avec les questions du dataset"""
    from src.chatbot import initialize_chatbot, chat, reset_memory

    # Charger le dataset
    dataset = load_test_dataset()
    test_cases = dataset["test_cases"]

    print("=" * 60)
    print("🧪 ÉVALUATION DU CHATBOT PULS-EVENTS")
    print("=" * 60)
    print(f"📊 Nombre de tests : {len(test_cases)}\n")

    # Initialiser le chatbot
    print("🚀 Initialisation du chatbot...")
    initialize_chatbot()
    print()

    results = []

    for i, test in enumerate(test_cases, 1):
        print(f"[Test {i}/{len(test_cases)}] {test['category']}")
        print(f"❓ Question : {test['question']}")

        # Poser la question
        response = chat(test['question'])
        print(f"🤖 Réponse : {response[:200]}...")

        # Vérifier si les mots-clés attendus sont présents
        expected = test.get("expected_answer_contains", [])
        response_lower = response.lower()
        
        matches = []
        for keyword in expected:
            # Gérer les alternatives (ex: "samedi|dimanche")
            if "|" in keyword:
                alternatives = keyword.split("|")
                if any(alt.lower() in response_lower for alt in alternatives):
                    matches.append(keyword)
            elif keyword.lower() in response_lower:
                matches.append(keyword)

        success = len(matches) >= len(expected) * 0.5  # Au moins 50% des mots-clés
        results.append(success)

        print(f"✅ Mots-clés trouvés : {matches}" if success else f"❌ Mots-clés manquants")
        print()

        # Tester le follow-up si présent
        if "follow_up" in test:
            print(f"   ↳ Follow-up : {test['follow_up']}")
            follow_response = chat(test['follow_up'])
            print(f"   🤖 Réponse : {follow_response[:150]}...")
            print()

        # Réinitialiser la mémoire pour le prochain test
        reset_memory()

    # Résultats finaux
    print("=" * 60)
    print("📊 RÉSULTATS")
    print("=" * 60)
    success_count = sum(results)
    total = len(results)
    score = (success_count / total) * 100
    
    print(f"✅ Tests réussis : {success_count}/{total}")
    print(f"📈 Score : {score:.1f}%")
    print()

    if score >= 80:
        print("🎉 Excellent ! Le chatbot répond de manière satisfaisante.")
    elif score >= 60:
        print("👍 Bien ! Quelques améliorations possibles.")
    else:
        print("⚠️ Des améliorations sont nécessaires.")

if __name__ == "__main__":
    evaluate_chatbot()