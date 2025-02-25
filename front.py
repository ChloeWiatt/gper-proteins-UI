import streamlit as st
from import_CSV import *

filters_uniprot = extract_filters()
#clés = champs, valeurs = liste des valeurs prises par nos données pour ce champ
filters_drugbank = {}
filters_pdb = {}
filters_chembl = {}
filtered_results = get_values_for_rows(filter_results(["Organism"], ["Homo sapiens (Human)"]),["Entry","Entry Name","Organism"])
print(filtered_results)

##Section 1 : barre latérale (filtres intelligents)

with st.sidebar:
    st.header("🔎 Filtres Avancés")
    
    # # Filtres multi-bases avec onglets
    uniprot, drugbank, pdb, chembl = st.tabs(["Uniprot", "DrugBank", "PDB", "ChEMBL"])

    with uniprot:
        uniprot_choices = []
        for key,values in filters_uniprot.items():
            with st.expander(key):
                uniprot_choices.append(st.multiselect("", options=values)) 
    
    with drugbank:
        drugbank_choices = []
        for key, values in filters_drugbank.items():
            with st.expander(key):
                drugbank_choices.append(st.multiselect("", options=values)) 

    with pdb:
        pdb_choices = []
        for key, values in filters_pdb.items():
            with st.expander(key):
                pdb_choices.append(st.multiselect("", options=values)) 

    with chembl:
        chembl_choices = []
        for key, values in filters_chembl.items():
            with st.expander(key):
                chembl_choices.append(st.multiselect("", options=values))

    #Autres modèles possibles
    # with uniprot:
    #     uniprot_choices2 = []
    #     for key, values in filters_uniprot.items():
    #         with st.expander(key):
    #             selected = [value for value in values if st.checkbox(value, key=f"uniprot_{key}_{value}")]
    #             uniprot_choices2.extend(selected)

    # with drugbank:
    #     with st.expander("💊 Caractéristiques"):
    #         drug_type_filter = st.selectbox("Type de molécule", ["1","2"])
    #         clinical_phase_filter = st.slider("Phase clinique", 0, 4)
            
    # with pdb:
    #     with st.expander("🔬 Résolution"):
    #         resolution_filter = st.slider("Résolution (Å)", 1.0, 5.0, (2.5, 3.5))
            
    # with chembl:
    #     with st.expander("⚗️ Propriétés"):
    #         admin_routes = st.multiselect("Voies d'administration", ["Oral", "Parenteral", "Topical"])



##Section 2 : zone principale (recherche et résultats)

# Barre de recherche universelle
search_query = st.text_input("🔍 Recherche par mot-clé, séquence ou formule", help="Ex: 'GPER1 human' ou 'C28H34N6O4S'")

# Grille de résultats interactifs
def show_details():
    print("Hello")

with st.container():
    st.subheader(f"📄 Résultats ({len(filtered_results)})")
    
    # Création des cartes cliquables
    with st.expander(f"🔬 {filtered_results['Entry Name']} | {filtered_results['Organism']}"):
            cols = st.columns([1,3,2])
            with cols[0]:
                st.image(filtered_results.get('preview_image', 'default_protein.png'))
            with cols[1]:
                st.markdown(f"**{filtered_results['Protein names']}**  \n`{filtered_results['Gene names']}`")
                st.caption(f"📏 Longueur: {filtered_results['Length']} | 🧬 Mass: {filtered_results['Mass']} kDa")
            with cols[2]:
                st.metric("Résolution", f"{filtered_results['resolution']} Å")
                st.button("Voir détails", key=filtered_results['id'], on_click=show_details, args=(filtered_results,))


##Section 3 : panneau de détails dynamique

if 'selected_result' in st.session_state:
    result = st.session_state.selected_result
    
    # Affichage ongleté des données
    uniprot, drugbank, pdb, chembl = st.tabs(["🧬 Structure", "💊 Pharmacologie", "🔬 Publications", "📊 Analytics"])
    
    with uniprot:
        # Visualisation 3D interactive
        view = py3Dmol.view(query=f'pdb:{result["pdb_id"]}')
        view.setStyle({'cartoon': {'color': 'spectrum'}})
        st.components.v1.html(view._make_html(), height=500)
        
        # Métriques structurelles
        cols = st.columns(3)
        cols[0].metric("Résolution", f"{result['resolution']} Å")
        cols[1].metric("Taxonomie", result['taxonomy'])
        cols[2].metric("Classification", result['enzyme_class'])
    
    with drugbank:
        # Données DrugBank avec gestion des valeurs manquantes
        if result.get('drugbank_data'):
            st.subheader("📈 Données Pharmacocinétiques")
            cols = st.columns(2)
            cols[0].metric("Demi-vie", result['half-life'] or "N/A")
            cols[1].metric("Liaison protéique", result['protein_binding'] or "N/A")
            
            st.subheader("⚠️ Effets Indésirables")
            st.graphviz_chart(create_toxicity_graph(result['toxicity_data']))
        else:
            st.warning("Aucune donnée DrugBank disponible")
    
    with pdb:
        # Publications avec intégration DOI
        for pub in result['publications']:
            st.markdown(f"""
            **{pub['title']}**  
            *{pub['authors']}*  
            DOI: [{pub['doi']}](https://doi.org/{pub['doi']})  
            PubMed: [{pub['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{pub['pmid']})
            """)
    
    with chembl:
        # Visualisations interactives
        st.plotly_chart(create_sequence_coverage_plot(result['sequence']))
        st.altair_chart(create_mass_vs_resolution_chart(result))