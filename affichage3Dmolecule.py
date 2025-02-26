import streamlit as st
import py3Dmol

# Titre de l'application
st.title("Visualisation 3D de Molécules")

# Code PDB de la molécule
pdb_code = "8xof"

# Créer la vue 3D avec py3Dmol
view = py3Dmol.view(query=f'pdb:{pdb_code}')
view.setStyle({'cartoon': {'color': 'spectrum'}})

# Générer le code HTML pour la visualisation 3D
html = view._make_html()  # Génère le code HTML/JavaScript pour la visualisation

# Afficher la visualisation 3D dans Streamlit
st.components.v1.html(html, width=800, height=600)