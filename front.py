import streamlit as st
from import_CSV import *
import py3Dmol
import re
import pandas as pd

# Extract filters and initialize filter dictionaries
filters_uniprot = extract_filters()
filters_drugbank = {}
filters_pdb = {}
filters_chembl = {}

# Define fields to display from Uniprot
uniprot_fields = [
    "Entry",
    "Entry Name", 
    "Protein names",
    "Gene Names",
    "Organism",
    "Sequence",
    "Length",
    "Mass",
    "Tissue specificity",
    "Subcellular location [CC]",
    "Function [CC]",
    "Involvement in disease",
    "Mutagenesis",
    "PubMed ID",
    "DOI ID",
    "PDB",
]

# Get filtered results
filtered_results = get_values_for_rows(
    filter_results(["Organism"], ["Homo sapiens (Human)"]), 
    uniprot_fields
)

## Section 1: Sidebar (intelligent filters)
with st.sidebar:
    st.header("🔎 Filtres Avancés")

    # Multi-database filters with tabs
    uniprot, drugbank, pdb, chembl = st.tabs(["Uniprot", "DrugBank", "PDB", "ChEMBL"])

    # Uniprot filters
    with uniprot:
        uniprot_choices = []
        for key, values in filters_uniprot.items():
            with st.expander(key):
                if key in ["Length", "Mass"]:
                    uniprot_choices.append(
                        st.slider(
                            "Select range",
                            min_value=min(values),
                            max_value=max(values),
                            value=(min(values), max(values)),
                        )
                    )
                else:
                    uniprot_choices.append(
                        st.multiselect(
                            f"Select {key}", 
                            options=values, 
                            label_visibility="collapsed"
                        )
                    )

    # DrugBank filters
    with drugbank:
        drugbank_choices = []
        for key, values in filters_drugbank.items():
            with st.expander(key):
                drugbank_choices.append(
                    st.multiselect(
                        f"Select {key}", 
                        options=values, 
                        label_visibility="collapsed"
                    )
                )

    # PDB filters
    with pdb:
        pdb_choices = []
        for key, values in filters_pdb.items():
            with st.expander(key):
                pdb_choices.append(
                    st.multiselect(
                        f"Select {key}", 
                        options=values, 
                        label_visibility="collapsed"
                    )
                )

    # ChEMBL filters
    with chembl:
        chembl_choices = []
        for key, values in filters_chembl.items():
            with st.expander(key):
                chembl_choices.append(
                    st.multiselect(
                        f"Select {key}", 
                        options=values, 
                        label_visibility="collapsed"
                    )
                )

## Section 2: Main area (search and results)

# Universal search bar
search_query = st.text_input(
    "🔍 Recherche par mot-clé, séquence ou formule",
    help="Ex: 'GPER1 human' ou 'C28H34N6O4S'",
)

# Display results count
results_number = len(list(filtered_results.values())[0])
with st.container():
    st.subheader(f"📄 Résultats ({results_number})")
    
    # Create clickable cards
    for i in range(results_number):
        with st.expander(f"{filtered_results['Entry Name'][i]}", expanded=False):
            for key, value in filtered_results.items():
                if key != "Entry" and key != "Entry Name":
                    if key == "PDB" and isinstance(value[i], str):
                        pdb_id = value[i].split(";")[0].strip('"')
                        view = py3Dmol.view(query=f"pdb:{pdb_id}")
                        view.setStyle({"cartoon": {"color": "spectrum"}})
                        st.components.v1.html(view._make_html(), height=500)
                    elif key == "Mutagenesis" and not(isinstance(value[i], float)):
                        # Parse mutagenesis data
                        mutations = []
                        raw_data = value[i].split("MUTAGEN ")
                        
                        for mut in raw_data:
                            if not mut.strip():
                                continue
                                
                            # Extract position and mutation
                            position_match = re.search(r'(\d+);', mut)
                            if position_match:
                                position = position_match.group(1)
                                
                            # Extract mutation details
                            mutation_match = re.search(r'\/note="([^"]+)"', mut)
                            if mutation_match:
                                mutation_details = mutation_match.group(1)
                                
                            # Extract evidence
                            evidence_match = re.search(r'\/evidence="([^"]+)"', mut)
                            evidence = evidence_match.group(1) if evidence_match else ""
                            
                            # Extract PubMed IDs from evidence
                            pubmed_ids = re.findall(r'PubMed:(\d+)', evidence) if evidence else []
                            
                            # Format PubMed links
                            pubmed_links = [f"[{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid})" for pmid in pubmed_ids]
                            pubmed_text = ", ".join(pubmed_links) if pubmed_links else "N/A"
                            
                            if position_match and mutation_match:
                                mutations.append({
                                    "Position": position,
                                    "Mutation": mutation_details,
                                    "Evidence": pubmed_text
                                })
                        
                        # Display as a table
                        if mutations:
                            st.markdown(f"**{key}**:")
                            st.table(pd.DataFrame(mutations))
                        else:
                            st.markdown(f"**{key}**: {value[i]}")
                    elif key != "PDB":
                        st.markdown(f"**{key}**: {value[i]}")

## Section 3: Dynamic details panel

if "selected_result" in st.session_state:
    result = st.session_state.selected_result

    # Tabbed display of data
    uniprot, drugbank, pdb, chembl = st.tabs(
        ["🧬 Structure", "💊 Pharmacologie", "🔬 Publications", "📊 Analytics"]
    )

    with uniprot:
        # Interactive 3D visualization
        view = py3Dmol.view(query=f'pdb:{result["pdb_id"]}')
        view.setStyle({"cartoon": {"color": "spectrum"}})
        st.components.v1.html(view._make_html(), height=500)

        # Structural metrics
        cols = st.columns(3)
        cols[0].metric("Résolution", f"{result['resolution']} Å")
        cols[1].metric("Taxonomie", result["taxonomy"])
        cols[2].metric("Classification", result["enzyme_class"])

    with drugbank:
        # DrugBank data with handling for missing values
        if result.get("drugbank_data"):
            st.subheader("📈 Données Pharmacocinétiques")
            cols = st.columns(2)
            cols[0].metric("Demi-vie", result["half-life"] or "N/A")
            cols[1].metric("Liaison protéique", result["protein_binding"] or "N/A")

            st.subheader("⚠️ Effets Indésirables")
            st.graphviz_chart(create_toxicity_graph(result["toxicity_data"]))
        else:
            st.warning("Aucune donnée DrugBank disponible")

    with pdb:
        # Publications with DOI integration
        for pub in result["publications"]:
            st.markdown(
                f"""
                **{pub['title']}**  
                *{pub['authors']}*  
                DOI: [{pub['doi']}](https://doi.org/{pub['doi']})  
                PubMed: [{pub['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{pub['pmid']})
                """
            )

    with chembl:
        # Interactive visualizations
        st.plotly_chart(create_sequence_coverage_plot(result["sequence"]))
        st.altair_chart(create_mass_vs_resolution_chart(result))