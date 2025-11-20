import os
os.system("pip install google-generativeai")

import streamlit as st
import google.generativeai as genai
import json
import random

# ==============================================================================
# 1. CONFIGURATION ET DONNÉES (ISSUES DE CONSTANTS.TS)
# ==============================================================================

st.set_page_config(page_title="Danse - Lycée Chevalier d'Eon", page_icon="💃", layout="wide")

# --- Consigne du Professeur (Votre System Instruction) ---
SYSTEM_INSTRUCTION = """
Tu es un professeur expert de "Danse d'expression" au Lycée Chevalier d'Eon.
Ta mission est d'aider les élèves de Seconde dans leur démarche de composition chorégraphique.

LA DÉMARCHE PÉDAGOGIQUE :
1. **L'Inducteur** : Le point de départ (Image, Lieu, Objet, Émotion...).
2. **Le Matériau** : Des gestes simples (Verbes d'action).
3. **Les Procédés** : Les outils de transformation (Canon, Miroir, Accumulation, Inversion...).
4. **Les Dominantes** : Les nuances (Espace, Temps, Énergie).

TON RÔLE :
- Suggérer des inducteurs originaux si l'élève sèche parmi la liste (Lieux, Animaux, Objets, Émotions...).
- Expliquer les procédés de composition (ex: "Le Canon, c'est comme 'Frère Jacques' mais avec le corps").
- Aider à enrichir une séquence en proposant des variations de vitesse, de niveau ou d'énergie.
- Encourager l'élève à justifier ses choix ("Pourquoi as-tu choisi le ralenti ici ?").

RÈGLES :
- Sois bienveillant, encourageant et concis.
- Utilise le vocabulaire spécifique (Inducteur, Procédé, Dominante, Kinesphère, Flux...).
"""

# --- Listes des options (Parameters Options) ---
PARAMETERS_OPTIONS = {
    'ESPACE': ['Niveau Haut', 'Niveau Bas', 'Au Sol', 'Extension', 'Regroupé', 'Diagonale', 'Cercle', 'Loin', 'Proche', 'Symétrie', 'Asymétrie', 'Trajet Direct', 'Trajet Courbe', 'Sur place'],
    'TEMPS': ['Ralenti', 'Accéléré', 'Arrêt/Silence', 'Saccadé', 'Pulsé', 'Continu', 'Vite', 'Canon', 'Polyrythmie', 'Unisson', 'Décalé', 'Ostinato', 'Progressif'],
    'ENERGIE': ['Fluide', 'Lourd', 'Léger', 'Sec', 'Explosif', 'Tendu', 'Relâché', 'Vibratoire', 'Suspendu', 'Percussif', 'Mou', 'Rebondi', 'Frotté', 'Caressé'],
    'RELATION': ['Unisson', 'Canon', 'Miroir', 'Contraste', 'Contact', 'Regard', 'Action/Réaction', 'Porté', 'Contrepoint', 'Question/Réponse', 'Opposition', 'Imitation', 'Poursuite']
}

# --- Données structurées pour les menus (Dance Elements) ---
DANCE_ELEMENTS = {
    "INDUCTEURS (Point de départ)": [
        "Lieux & Environnements", "Le Vivant (Animaux & Nature)", "Culture, Histoire & Personnages", 
        "Objets & Accessoires", "Sensations & Abstrait", "Styles & Techniques"
    ],
    "PROCÉDÉS (Transformation)": [
        "Le Canon", "Vitesse & Durée", "Répétition", "Accumulation", 
        "Miroir & Symétrie", "Cascade", "Relations & Contacts", 
        "Transformations & Variations", "Collage & Rupture"
    ],
    "ENRICHISSEMENT (Dominantes)": [
        "Le Corps", "L'Espace", "Le Temps", "L'Énergie", "La Relation"
    ]
}

# ==============================================================================
# 2. CONNEXION API SÉCURISÉE (Ajout de la gestion d'erreurs)
# ==============================================================================

model = None
try:
    # 1. Tente de récupérer la clé dans les Streamlit Secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # 2. Configure le modèle avec la System Instruction
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTION)
    API_SUCCESS = True
except KeyError:
    API_SUCCESS = False
    # Ce message d'erreur est affiché SI le fichier est installé, mais la clé est absente.
    st.error("Erreur de configuration API: La clé 'GOOGLE_API_KEY' n'est pas configurée dans les Streamlit Secrets. Veuillez vérifier les 'Advanced settings' et vous assurer que la clé y est complète et au format correct (entre guillemets).")
except Exception as e:
    API_SUCCESS = False
    # Ce message d'erreur est affiché en cas d'échec de connexion inattendu
    st.error(f"Erreur de connexion inattendue avec Google Gemini: {e}")
        
# Si l'API n'a pas pu se connecter, on arrête l'exécution pour éviter les erreurs plus bas
if not API_SUCCESS:
    st.stop()


# ==============================================================================
# 3. INTERFACE UTILISATEUR (TABS)
# ==============================================================================

st.title("Danse d'Expression - Lycée Chevalier d'Eon 💃")
st.markdown("---")

# Création des onglets
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Le Coach", 
    "✨ Générateur Choré", 
    "🛠️ Atelier Variations", 
    "💡 Boîte à Idées"
])

# ------------------------------------------------------------------------------
# TAB 1: LE COACH (CHATBOT)
# ------------------------------------------------------------------------------
with tab1:
    st.header("Discussion avec le Coach")
    st.info("Pose tes questions sur ton projet, tes doutes ou demande une explication.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "model", "parts": ["Bonjour ! Je suis ton coach de danse. Sur quoi travailles-tu aujourd'hui ?"]})

    for message in st.session_state.messages:
        role = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(message["parts"][0])

    if prompt := st.chat_input("Écris ton message ici..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "parts": [prompt]})

        try:
            chat = model.start_chat(history=st.session_state.messages)
            response = chat.send_message(prompt)
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
        except Exception as e:
            st.error(f"Erreur lors de l'envoi du message : {e}")

# ------------------------------------------------------------------------------
# TAB 2: GÉNÉRATEUR DE CHORÉGRAPHIE
# ------------------------------------------------------------------------------
with tab2:
    st.header("Générateur de Séquence")
    st.caption("Propose un thème et des contraintes, l'IA te propose 4 mouvements.")

    col1, col2 = st.columns(2)
    with col1:
        theme_input = st.text_input("Thème de la chorégraphie", placeholder="ex: La tempête, L'attente...")
    
    with col2:
        # Sélection multiple des contraintes
        contraintes_temps = st.multiselect("Contraintes TEMPS", PARAMETERS_OPTIONS['TEMPS'])
        contraintes_energie = st.multiselect("Contraintes ÉNERGIE", PARAMETERS_OPTIONS['ENERGIE'])
        contraintes_espace = st.multiselect("Contraintes ESPACE", PARAMETERS_OPTIONS['ESPACE'])
    
    all_constraints = contraintes_temps + contraintes_energie + contraintes_espace

    if st.button("Générer la proposition", type="primary"):
        if not theme_input:
            st.warning("Merci d'indiquer un thème.")
        else:
            with st.spinner("Le coach réfléchit..."):
                prompt_chore = f"""
                Thème: {theme_input}
                Contraintes imposées: {', '.join(all_constraints)}
                
                Propose une séquence de 4 mouvements enchainés qui respecte ce thème et ces contraintes.
                Décris chaque mouvement avec : Action (Verbe), Espace, Temps, Énergie.
                Format: Liste à puces claire.
                """
                try:
                    response = model.generate_content(prompt_chore)
                    st.success("Voici une proposition de séquence :")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")

# ------------------------------------------------------------------------------
# TAB 3: ATELIER VARIATIONS
# ------------------------------------------------------------------------------
with tab3:
    st.header("Travailler un Élément Précis")
    st.caption("Tu bloques sur un élément ? Demande 3 exercices ou variations.")

    cat_choice = st.selectbox("Quelle catégorie travailles-tu ?", list(DANCE_ELEMENTS.keys()))
    elem_choice = st.selectbox("Quel élément précis ?", DANCE_ELEMENTS[cat_choice])

    if st.button(f"Trouver des variations pour : {elem_choice}"):
        with st.spinner("Recherche d'exercices..."):
            prompt_var = f"""
            Tu es un professeur de danse. Donne-moi 3 idées d'exercices ou de variations originales et concrètes pour travailler : "{elem_choice}" (Catégorie: {cat_choice}) avec des élèves de lycée.
            Sois bref, précis et imaginatif.
            Format attendu : Une liste simple de 3 points.
            """
            try:
                response = model.generate_content(prompt_var)
                st.markdown(f"### 3 Idées pour : {elem_choice}")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erreur lors de la recherche : {e}")

# ------------------------------------------------------------------------------
# TAB 4: BOÎTE À IDÉES (CRÉATIVITÉ)
# ------------------------------------------------------------------------------
with tab4:
    st.header("Panne d'inspiration ?")
    
    idea_type = st.radio("De quoi as-tu besoin ?", ["Inducteur (Thème de départ)", "Procédé (Idée de transformation)"], horizontal=True)
    
    if st.button("Surprends-moi ! ✨"):
        with st.spinner("Invocation de la muse de la danse..."):
            prompt_idea = ""
            if "Inducteur" in idea_type:
                prompt_idea = "Propose une idée d'Inducteur (thème de départ) très originale pour une chorégraphie de lycée. Donne un Titre court et une description inspirante en une phrase."
            else:
                prompt_idea = "Propose une idée créative pour transformer un geste simple (Procédé de composition) de manière originale. Donne un Titre court et une consigne précise en une phrase."
            
            # On demande du JSON pour un affichage propre
            prompt_full = prompt_idea + " Réponds uniquement au format JSON avec les clés 'title' et 'description'."
            
            try:
                response = model.generate_content(prompt_full)
                # Nettoyage sommaire pour extraire le JSON
                text_resp = response.text
                start = text_resp.find('{')
                end = text_resp.rfind('}') + 1
                json_str = text_resp[start:end]
                
                data = json.loads(json_str)
                
                st.markdown(f"## 🎭 {data.get('title', 'Idée Originale')}")
                st.info(data.get('description', ''))
                
            except Exception as e:
                st.error(f"Erreur lors de la génération de l'idée : {e}")
