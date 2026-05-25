import streamlit as st
import re
import pandas as pd
import io
import json
import os

COUNTER_FILE = "click_counter.json"

def get_click_count():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            try:
                data = json.load(f)
                return data.get("clicks", 0)
            except (json.JSONDecodeError, ValueError):
                return 0
    return 0

def increment_click_count():
    count = get_click_count() + 1
    with open(COUNTER_FILE, "w") as f:
        json.dump({"clicks": count}, f)
    return count

st.set_page_config(
    page_title="Kub Tools - Extracteur Dofusbook", 
    page_icon="⚙️",
    initial_sidebar_state="collapsed"
)

st.title("⚙️ Kub Tools - Extracteur d'Items Dofusbook")
st.markdown("""
Cet outil te permet d'extraire rapidement les informations (Nom, Type, Niveau) de ton atelier Dofusbook sous forme de tableau ou de fichier CSV.

**Comment l'utiliser :**
1. Va sur la page de ton atelier Dofusbook.
2. Sélectionne tout le texte de la page (Ctrl+A ou Cmd+A) ou juste la liste des items.
3. Copie (Ctrl+C ou Cmd+C).
4. Colle le texte dans la boîte ci-dessous.

📺 **Soutiens le projet et rejoins la communauté en t'abonnant à [ma chaîne YouTube Kub-df](https://www.youtube.com/@Kub-df/) !**
""")

raw_text = st.text_area("Colle ton texte Dofusbook ici :", height=200)

if st.button("Extraire les items"):
    increment_click_count()
    if raw_text.strip():
        lines = raw_text.split('\n')
        items = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # On repere le "x" qui precede la quantite
            if line == 'x' and i > 0 and i < len(lines) - 2:
                name = lines[i-1].strip()
                quantity_raw = lines[i+1].strip()
                type_level_raw = lines[i+2].strip()
                
                try:
                    quantity = int(quantity_raw)
                except ValueError:
                    quantity = 1
                
                # On extrait le type et le niveau
                match = re.search(r'(.+?) - Niveau (\d+)', type_level_raw)
                if match:
                    item_type = match.group(1).strip()
                    level = match.group(2).strip()
                    
                    # Regroupement de toutes les armes
                    armes_types = ["Hache", "Faux", "Pioche", "Marteau", "Pelle", "Dagues", "Arc", "Épée", "Bâton", "Baguette", "Lance"]
                    if item_type in armes_types:
                        item_type = "Arme"
                    
                    items.append({
                        "Nom": name,
                        "Nombre": quantity,
                        "Type": item_type,
                        "Niveau": int(level)
                    })
        
        if items:
            st.success(f"{len(items)} items extraits avec succès !")
            
            # Affichage sous forme de DataFrame (Tableau)
            df = pd.DataFrame(items)
            st.dataframe(df, use_container_width=True)
            
            # Bouton pour télécharger en CSV
            csv = df.to_csv(index=False, sep=';').encode('utf-8-sig')
            
            st.download_button(
                label="📥 Télécharger le fichier CSV",
                data=csv,
                file_name='dofusbook_items.csv',
                mime='text/csv',
            )
        else:
            st.warning("Aucun item n'a pu être trouvé. Assure-toi d'avoir bien copié les données de ton atelier Dofusbook.")
    else:
        st.error("Le champ de texte est vide.")

st.sidebar.markdown("### 📊 Statistiques")
st.sidebar.text(f"Outil utilisé {get_click_count()} fois")
