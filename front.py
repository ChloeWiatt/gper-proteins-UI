import streamlit as st
import requests

st.title("Interface de Recherche pour GPER")

st.sidebar.header("Filtres de Recherche")

# --- Filtres d'identification et classification ---
gene_names = st.sidebar.text_input("Nom du gène (ex: GPER1)")
organism = st.sidebar.selectbox("Organisme", options=["", "Homo sapiens", "Mus musculus"])

# --- Filtres de structure et séquence ---
ptm = st.sidebar.text_input("Modification post-traductionnelle (ex: phosphorylation)")
pdb = st.sidebar.text_input("ID de structure PDB (ex: 1XYZ)")

# --- Filtres par médicaments ---
medication_name = st.sidebar.text_input("Nom du médicament (ex: Tamoxifène)")
medication_interaction = st.sidebar.selectbox("Type d'interaction médicamenteuse", options=["", "Agoniste", "Antagoniste", "Modulateur"])

if st.sidebar.button("Rechercher"):
    # Préparation des paramètres pour l'appel à l'API Flask
    params = {
        "gene_names": gene_names,
        "organism": organism,
        "ptm": ptm,
        "pdb": pdb,
        "medication_name": medication_name,
        "medication_interaction": medication_interaction
    }
    
    try:
        response = requests.get("http://localhost:5000/query", params=params)
        if response.status_code == 200:
            results = response.json()
            st.write("### Résultats de la recherche")
            if results:
                for entry in results:
                    st.markdown(f"**Accession Uniprot :** {entry.get('accession', 'N/A')}")
                    st.markdown(f"**Nom de la protéine :** {entry.get('protein_name', 'N/A')}")
                    # Affichage du ou des noms de gènes
                    genes = entry.get('genes', [])
                    if genes:
                        gene_str = ", ".join([g.get("value", "") for g in genes])
                    else:
                        gene_str = "N/A"
                    st.markdown(f"**Nom(s) du gène :** {gene_str}")
                    st.markdown(f"**Organisme :** {entry.get('organism_name', 'N/A')}")
                    sequence = entry.get('sequence', '')
                    st.markdown(f"**Séquence (troncature) :** {sequence[:50] + '...' if sequence else 'N/A'}")
                    st.markdown(f"**Longueur :** {entry.get('length', 'N/A')} aa")
                    
                    # Affichage des références PDB
                    pdb_refs = entry.get('xref_pdb', [])
                    if pdb_refs:
                        pdb_list = ", ".join(pdb_refs)
                    else:
                        pdb_list = "N/A"
                    st.markdown(f"**Structures PDB :** {pdb_list}")
                    
                    # Affichage des médicaments associés (issus de ChEMBL)
                    st.markdown("**Médicaments associés :**")
                    medications = entry.get("medications", [])
                    if medications:
                        for med in medications:
                            st.markdown(f"- **Nom :** {med.get('name', 'N/A')} | **Affinité :** {med.get('affinity', 'N/A')} | **Interaction :** {med.get('interaction', 'N/A')} | **Phase :** {med.get('phase', 'N/A')} | **Indication :** {med.get('indication', 'N/A')}")
                    else:
                        st.markdown("Aucune donnée médicamenteuse disponible.")
                    
                    st.markdown("---")
            else:
                st.warning("Aucun résultat trouvé pour les filtres sélectionnés.")
        else:
            st.error("Erreur lors de la récupération des données depuis l'API Flask.")
    except Exception as e:
        st.error(f"Erreur de connexion à l'API Flask: {e}")
