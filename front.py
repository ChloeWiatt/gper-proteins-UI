import streamlit as st
from import_CSV import *
import py3Dmol
import re
import pandas as pd
from subcell_visualization import display_subcellular_location

# Extract filters and initialize filter dictionaries
filters_uniprot = extract_filters_uniprot()
filters_drugbank = extract_filters_drugbank()
filters_pdb = {}
filters_chembl = {}

# Define fields to display
uniprot_selections = [
    "Entry",
    "Entry Name",
    "Protein names",
    "Gene Names",
    "Organism",
    "Sequence",
    "Length",
    "Mass",
    "Tissue specificity",
    "Function [CC]",
    "Subcellular location [CC]",
    "Involvement in disease",
    "Mutagenesis",
    "PubMed ID",
    "PDB",
    "AlphaFoldDB",
]

st.set_page_config(page_title="GPCR-GPER Data Explorer")
drugbank_selections = [
    "DrugBank ID",
    "Name",
    "Type",
    "Groups",
    "Description",
    "Synonyms",
    "Brand Names",
    "Indication",
    "Pharmacodynamics",
    "Mechanism of Action",
    "Absorption",
    "Metabolism",
    "Route of Elimination",
    "Protein Binding",
    "Drug Interactions",
    "Food Interactions",
    "Affected Organisms",
    "Chemical Formula",
    "Molecular Weight",
    "IUPAC Name",
    "CAS Number",
    "SMILES",
    "InChI",
    "InChIKey",
    "UNII",
    "ATC Codes",
    "Patents",
    "Spectra",
]

## Section 1: Sidebar (intelligent filters)
with st.sidebar:
    st.header("🔎 Advanced search")

    # Add attribute presence filter expander
    with st.expander("✅ Filter by Attribute Presence"):
        st.markdown("**Show only entries with:**")

        # Initialize presence filters in session state if not exists
        if "presence_filters" not in st.session_state:
            st.session_state.presence_filters = {}

        # Key attributes to filter by presence/absence
        key_attributes = {
            "has_structure": "3D Structure available (PDB)",
            "has_disease": "Disease involvement",
            "has_mutations": "Mutation data",
            "has_function": "Functional annotation",
            "has_tissue": "Tissue specificity",
        }

        # Create a checkbox for each attribute
        for key, label in key_attributes.items():
            st.session_state.presence_filters[key] = st.checkbox(label)

    # Multi-database filters with tabs
    uniprot, drugbank, pdb, chembl = st.tabs(["Uniprot", "DrugBank", "PDB", "ChEMBL"])

    # Uniprot filters
    with uniprot:
        uniprot_choices = {}
        expanders = {
            "ℹ️ General informations": [
                "Entry",
                "Entry Name",
                "Protein names",
                "Organism",
            ],
            "🧬 Genome": ["Gene Names", "Sequence"],
            "🔢 Numericals": ["Length", "Mass"],
        }

        for expander, keys in expanders.items():
            with st.expander(expander):
                for key in keys:
                    if key == "Mass":
                        st.markdown(f"**{key} (Da)**")
                    else:
                        st.markdown(f"**{key}**")

                    if key == "Sequence":
                        # Champ de texte pour la recherche de séquence
                        sequence_query = st.text_input(
                            "Enter sequence or partial sequence",
                            key="sequence_search",
                            help="Enter a sequence pattern to find (e.g., 'AAA')",
                        )
                        uniprot_choices.update({"Sequence": sequence_query})
                    elif key in ["Length", "Mass"]:
                        values = filters_uniprot[key]
                        uniprot_choices.update(
                            {
                                key: st.slider(
                                    "Select range",
                                    min_value=min(values),
                                    max_value=max(values),
                                    value=(min(values), max(values)),
                                )
                            }
                        )
                    else:
                        values = filters_uniprot[key]
                        uniprot_choices.update(
                            {
                                key: st.multiselect(
                                    f"Select {key}",
                                    options=values,
                                    label_visibility="collapsed",
                                )
                            }
                        )

    # DrugBank filters
    with drugbank:
        drugbank_choices = {}
        expanders = {
            "💊 General": [
                "DrugBank ID",
                "Name",
                "Type",
                "Groups",
                "Synonyms",
                "Brand Names",
            ],
            "📊 Properties": [
                "Absorption",
                "Protein Binding",
                "Molecular Weight",
            ],
            "🧪 Chemistry": [
                "Chemical Formula",
                "IUPAC Name",
                "CAS Number",
                "InChIKey",
                "UNII",
            ],
            "🏥 Clinical": [
                "ATC Codes",
                "Food Interactions",
                "Affected Organisms",
                "Patents",
                "Spectra",
            ],
        }

        for expander, keys in expanders.items():
            with st.expander(expander):
                for key in keys:
                    st.markdown(f"**{key}**")

                    if key in filters_drugbank:
                        values = filters_drugbank[key]

                        if key in ["Absorption", "Protein Binding", "Molecular Weight"]:
                            # Gérer les filtres numériques avec des sliders
                            if values:
                                drugbank_choices.update(
                                    {
                                        key: st.slider(
                                            f"Select {key} range",
                                            min_value=min(values),
                                            max_value=max(values),
                                            value=(min(values), max(values)),
                                            step=(
                                                0.1
                                                if key != "Molecular Weight"
                                                else 1.0
                                            ),
                                        )
                                    }
                                )
                        else:
                            # Multiselect pour tous les autres filtres
                            drugbank_choices.update(
                                {
                                    key: st.multiselect(
                                        f"Select {key}",
                                        options=values,
                                        label_visibility="collapsed",
                                    )
                                }
                            )

    # PDB filters
    with pdb:
        pdb_choices = []
        for key, values in filters_pdb.items():
            with st.expander(key):
                pdb_choices.append(
                    st.multiselect(
                        f"Select {key}", options=values, label_visibility="collapsed"
                    )
                )

    # ChEMBL filters
    with chembl:
        chembl_choices = []
        for key, values in filters_chembl.items():
            with st.expander(key):
                chembl_choices.append(
                    st.multiselect(
                        f"Select {key}", options=values, label_visibility="collapsed"
                    )
                )

## Section 2: Main area (search and results)
# Get filtered results
print(uniprot_choices)
filtered_uniprot_indices = filter_results_uniprot(uniprot_choices)
filtered_results = get_values_for_rows_uniprot(
    filtered_uniprot_indices, uniprot_selections
)

# Display results count
results_number = len(list(filtered_results.values())[0])

# Initialize session state for detail view if not exists
if "show_detail_view" not in st.session_state:
    st.session_state.show_detail_view = False
if "selected_protein" not in st.session_state:
    st.session_state.selected_protein = None


# Function to handle button click
def show_protein_detail(protein_index):
    st.session_state.selected_protein = protein_index
    st.session_state.show_detail_view = True


# Add this before the results display section
# Filter results based on attribute presence checkboxes
if "presence_filters" in st.session_state:
    indices_to_keep = []
    for i in range(results_number):
        include_row = True

        # Check if the presence filters require this row to be filtered out
        if st.session_state.presence_filters.get("has_structure", False):
            if (
                "PDB" not in filtered_results
                or pd.isna(filtered_results["PDB"][i])
                or filtered_results["PDB"][i] == ""
            ):
                include_row = False

        if include_row and st.session_state.presence_filters.get("has_disease", False):
            if (
                "Involvement in disease" not in filtered_results
                or pd.isna(filtered_results["Involvement in disease"][i])
                or filtered_results["Involvement in disease"][i] == ""
            ):
                include_row = False

        if include_row and st.session_state.presence_filters.get(
            "has_mutations", False
        ):
            if (
                "Mutagenesis" not in filtered_results
                or pd.isna(filtered_results["Mutagenesis"][i])
                or filtered_results["Mutagenesis"][i] == ""
            ):
                include_row = False

        if include_row and st.session_state.presence_filters.get("has_function", False):
            if (
                "Function [CC]" not in filtered_results
                or pd.isna(filtered_results["Function [CC]"][i])
                or filtered_results["Function [CC]"][i] == ""
            ):
                include_row = False

        if include_row and st.session_state.presence_filters.get("has_location", False):
            if (
                "Subcellular location [CC]" not in filtered_results
                or pd.isna(filtered_results["Subcellular location [CC]"][i])
                or filtered_results["Subcellular location [CC]"][i] == ""
            ):
                include_row = False

        if include_row and st.session_state.presence_filters.get("has_tissue", False):
            if (
                "Tissue specificity" not in filtered_results
                or pd.isna(filtered_results["Tissue specificity"][i])
                or filtered_results["Tissue specificity"][i] == ""
            ):
                include_row = False

        if include_row:
            indices_to_keep.append(i)

    # Create filtered version of results
    if any(st.session_state.presence_filters.values()):
        filtered_display_results = {}
        for key, values in filtered_results.items():
            filtered_display_results[key] = [values[i] for i in indices_to_keep]
        filtered_results = filtered_display_results
        # Update results number for display
        results_number = len(indices_to_keep)

# Filter results based on sequence query
if "Sequence" in uniprot_choices and uniprot_choices["Sequence"]:
    sequence_query = uniprot_choices["Sequence"].upper().strip()

    # Vérifier si nous avons réellement le champ Sequence dans les données
    if not (
        "Sequence" not in filtered_results or len(filtered_results["Sequence"]) == 0
    ):
        # Si nous avons des séquences, procéder à la recherche
        indices_to_keep = []

        for i in range(results_number):
            if pd.isna(filtered_results["Sequence"][i]):
                continue

            # Nettoyer la séquence (enlever espaces, sauts de ligne)
            clean_seq = "".join(filtered_results["Sequence"][i].split())

            # Vérifier si la séquence contient la sous-séquence recherchée
            if sequence_query in clean_seq.upper():
                indices_to_keep.append(i)

        # Met à jour les résultats filtrés
        if indices_to_keep:
            st.success(f"Found in {len(indices_to_keep)} sequence(s)")
            filtered_display_results = {}
            for key, values in filtered_results.items():
                filtered_display_results[key] = [values[i] for i in indices_to_keep]
            filtered_results = filtered_display_results
            # Met à jour le nombre de résultats
            results_number = len(indices_to_keep)
        elif sequence_query:  # Si aucune correspondance n'a été trouvée
            st.warning(f"Aucune séquence contenant '{sequence_query}' trouvée.")
            results_number = 0

# Ajouter cette section après le filtrage UniProt pour récupérer les résultats filtrés de DrugBank
filtered_drugbank_results = {}
if drugbank_choices:
    print(drugbank_choices)
    filtered_drugbank_indices = filter_results_drugbank(drugbank_choices)
    filtered_drugbank_results = get_values_for_rows_drugbank(filtered_uniprot_indices,filtered_drugbank_indices,drugbank_selections)
    print(filtered_drugbank_results)
    drugbank_results_number = len(filtered_drugbank_indices)


# Then continue with your existing code to display results
# Main view - either results listing or detail page
if not st.session_state.show_detail_view:
    with st.container():
        st.subheader(f"📄 Results ({results_number})")

        # Create clickable cards
        for i in range(results_number):
            with st.expander(f"{filtered_results['Entry Name'][i]}", expanded=False):
                # Add view details button
                col1, col2 = st.columns([3, 1])
                with col2:
                    st.button(
                        f"📋 View Details",
                        key=f"detail_btn_{i}",
                        on_click=show_protein_detail,
                        args=(i,),
                    )

                # Display protein information
                for key in ["Entry", "Protein names", "Gene Names", "Organism"]:
                    if key in filtered_results:
                        value = filtered_results[key]
                        if key != "Entry Name":
                            if isinstance(value[i], float):
                                continue
                            elif key == "PDB":
                                pdb_id = value[i].split(";")[0].strip('"')
                                view = py3Dmol.view(query=f"pdb:{pdb_id}")
                                view.setStyle({"cartoon": {"color": "spectrum"}})
                                st.components.v1.html(view._make_html(), height=500)
                            elif key != "PDB":
                                st.markdown(f"**{key}**: {value[i]}")
else:
    # Detail view for selected protein
    protein_idx = st.session_state.selected_protein

    # Back button
    if st.button("← Back to results"):
        st.session_state.show_detail_view = False
        st.rerun()
    # Create tabs for different databases
    uniprot_tab, drugbank_tab, pdb_tab, chembl_tab = st.tabs(
        ["🧬 UniProt", "💊 DrugBank", "🔬 3D Structure", "🧪 ChEMBL"]
    )

    with uniprot_tab:
        st.subheader("UniProt Information")

        # Display all UniProt fields for the selected protein
        for field in uniprot_selections:
            if field in filtered_results and protein_idx < len(filtered_results[field]):
                value = filtered_results[field][protein_idx]

                # Skip empty, None or NaN values
                if value != value or value is None or pd.isna(value) or value == "":
                    continue

                # Special handling for certain fields
                if field == "Sequence":
                    with st.expander("Sequence"):
                        st.text(value)
                elif field == "Mutagenesis":
                    # Use existing mutagenesis parsing logic if needed
                    st.markdown(f"**{field}:**")
                    # Parse mutagenesis data
                    mutations = []
                    raw_data = value.split("MUTAGEN ")

                    for mut in raw_data:
                        if not mut.strip():
                            continue

                        # Extract position and mutation
                        position_match = re.search(r"(\d+);", mut)
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
                        pubmed_ids = (
                            re.findall(r"PubMed:(\d+)", evidence) if evidence else []
                        )

                        # Format PubMed links with HTML for dataframe display
                        pubmed_html_links = []
                        for pmid in pubmed_ids:
                            pubmed_html_links.append(
                                f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}" target="_blank">{pmid}</a>'
                            )

                        pubmed_text = (
                            ", ".join(pubmed_html_links) if pubmed_html_links else "N/A"
                        )

                        if position_match and mutation_match:
                            mutations.append(
                                {
                                    "Position": position,
                                    "Mutation": mutation_details,
                                    "Evidence": pubmed_text,
                                }
                            )

                    # Display as a dataframe with clickable links
                    if mutations:
                        df = pd.DataFrame(mutations)
                        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
                elif field == "Mass":
                    st.markdown(f"**{field}:** {value} Da")
                elif field == "Tissue specificity":
                    # Remove the "TISSUE SPECIFICITY: " prefix and any trailing periods
                    cleaned_value = value.replace("TISSUE SPECIFICITY: ", "").strip()
                    cleaned_value = re.sub(r"\.$", "", cleaned_value).strip()

                    # Extract all PubMed IDs
                    pubmed_matches = re.findall(
                        r"ECO:0000269\|PubMed:(\d+)", cleaned_value
                    )
                    if pubmed_matches:
                        # Remove the entire ECO reference section
                        cleaned_value = re.sub(r"{ECO:.*}", "", cleaned_value).strip()
                        # Display the cleaned text
                        st.markdown(f"**{field}:** {cleaned_value}")
                        # Create links for all PubMed references
                        pubmed_links = [
                            f"[{id}](https://pubmed.ncbi.nlm.nih.gov/{id})"
                            for id in pubmed_matches
                        ]
                        st.markdown(f"🔗 PubMed References: {', '.join(pubmed_links)}")
                    else:
                        st.markdown(f"**{field}:** {cleaned_value}")
                elif field == "Function [CC]":
                    # Remove the "FUNCTION: " prefix and any trailing periods
                    cleaned_value = value.replace("FUNCTION: ", "").strip()
                    cleaned_value = re.sub(r"\.$", "", cleaned_value).strip()

                    # Extract all PubMed IDs
                    pubmed_matches = re.findall(r"PubMed:(\d+)", cleaned_value)
                    if pubmed_matches:
                        # Remove the entire ECO reference section
                        cleaned_value = re.sub(r"{ECO:.*?}", "", cleaned_value).strip()
                        # Clean up any remaining parenthetical PubMed references
                        cleaned_value = re.sub(
                            r"\(PubMed:[0-9,\s]+\)", "", cleaned_value
                        ).strip()
                        # Display the cleaned text
                        st.markdown(f"**{field}:** {cleaned_value}")
                        # Create links for all PubMed references
                        pubmed_links = [
                            f"[{id}](https://pubmed.ncbi.nlm.nih.gov/{id})"
                            for id in pubmed_matches
                        ]
                        st.markdown(f"🔗 PubMed References: {', '.join(pubmed_links)}")
                    else:
                        st.markdown(f"**{field}:** {cleaned_value}")

                elif field == "Involvement in disease":
                    # Remove the "DISEASE: " prefix and any trailing periods
                    cleaned_value = value.replace("DISEASE: ", "").strip()
                    cleaned_value = re.sub(r"\.$", "", cleaned_value).strip()

                    # Extract all PubMed IDs
                    pubmed_matches = re.findall(r"PubMed:(\d+)", cleaned_value)
                    if pubmed_matches:
                        # Remove the entire ECO reference section
                        cleaned_value = re.sub(r"{ECO:.*?}", "", cleaned_value).strip()
                        # Remove MIM reference but keep the number
                        cleaned_value = re.sub(
                            r"\[MIM:(\d+)\]", r"(MIM: \1)", cleaned_value
                        )
                        # Display the cleaned text
                        st.markdown(f"**{field}:** {cleaned_value}")
                        # Create links for all PubMed references
                        pubmed_links = [
                            f"[{id}](https://pubmed.ncbi.nlm.nih.gov/{id})"
                            for id in pubmed_matches
                        ]
                        st.markdown(f"🔗 PubMed References: {', '.join(pubmed_links)}")
                    else:
                        st.markdown(f"**{field}:** {cleaned_value}")
                elif field == "Subcellular location [CC]":
                    # st.markdown(f"**{field}:** {value}")
                    # Add the visualization below the text
                    st.markdown("### Subcellular Location Visualization")
                    display_subcellular_location(value)
                elif field == "PDB":
                    continue
                elif field == "PubMed ID":
                    # Split the PubMed IDs and clean them
                    pubmed_ids = [
                        pid.strip() for pid in value.split(";") if pid.strip()
                    ]

                    # Create the links
                    st.markdown(f"**{field}:**")
                    pubmed_links = []
                    for pid in pubmed_ids:
                        pubmed_links.append(
                            f"[{pid}](https://pubmed.ncbi.nlm.nih.gov/{pid})"
                        )

                    # Display all links with commas between them
                    st.markdown(", ".join(pubmed_links))
                else:
                    st.markdown(f"**{field}:** {value}")
                st.divider()  # Add a divider between fields

    with drugbank_tab:
        st.subheader("DrugBank Information")

        if not filtered_drugbank_results:
            st.info("No DrugBank data available for this protein.")
        else:
            # Afficher les données DrugBank
            for field in drugbank_selections:
                if (
                    field in filtered_drugbank_results
                    and len(filtered_drugbank_results[field]) > 0
                ):
                    value = filtered_drugbank_results[field][
                        0
                    ]  # Prendre la première entrée correspondante

                    # Ignorer les valeurs vides
                    if pd.isna(value) or value == "":
                        continue

                    # Formatage spécial pour certains champs
                    if field == "Molecular Weight":
                        st.markdown(f"**{field}:** {value} Da")
                    elif field == "Chemical Formula":
                        # Afficher la formule chimique avec mise en forme
                        formula = re.sub(r"(\d+)", r"<sub>\1</sub>", value)
                        st.markdown(f"**{field}:** {formula}", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{field}:** {value}")

                    st.divider()

    with pdb_tab:
        st.subheader("3D Structures View")

        # Check PDB first
        pdb_value = filtered_results.get("PDB", [None])[protein_idx]
        alphafold_value = filtered_results.get("AlphaFoldDB", [None])[protein_idx]

        if not pd.isna(pdb_value) and pdb_value:
            st.markdown("### PDB Structure")
            pdb_id = pdb_value.split(";")[0].strip('"')
            view = py3Dmol.view(query=f"pdb:{pdb_id}")
            view.setStyle({"cartoon": {"color": "spectrum"}})
            st.components.v1.html(view._make_html(), height=500)

        # Check AlphaFold
        if not pd.isna(alphafold_value) and alphafold_value:
            st.markdown("### AlphaFold Structure")
            # AlphaFold IDs are UniProt accessions
            alphafold_id = alphafold_value.strip()

            # If no specific ID provided, use the Entry ID
            if not alphafold_id and "Entry" in filtered_results:
                alphafold_id = filtered_results["Entry"][protein_idx]

            if alphafold_id:
                try:
                    # Clean the ID - remove any trailing characters like semicolons
                    clean_id = alphafold_id.split(";")[0].strip()

                    # Load from AlphaFoldDB using the UniProt ID
                    alphafold_url = f"https://alphafold.ebi.ac.uk/files/AF-{clean_id}-F1-model_v4.pdb"
                    st.info(f"Loading AlphaFold structure: {clean_id}")

                    # Create a direct download link for debugging
                    st.markdown(f"[Direct PDB download]({alphafold_url})")

                    # Use a different approach to load the model
                    view = py3Dmol.view(width=700, height=500)

                    # Option 1: Use fetch to load the structure
                    # Note: Using the full URL was causing issues, so we'll use the direct file download approach
                    import requests

                    try:
                        response = requests.get(alphafold_url)
                        if response.status_code == 200:
                            pdb_data = response.text
                            view.addModel(pdb_data, "pdb")
                            view.setStyle({"cartoon": {"colorscheme": "rainbow"}})
                            view.zoomTo()
                            view.spin(True)
                            st.components.v1.html(view._make_html(), height=500)

                            # Add a link to the AlphaFold database
                            st.markdown(
                                f"[View on AlphaFold DB](https://alphafold.ebi.ac.uk/entry/{clean_id})"
                            )
                        else:
                            st.error(
                                f"Failed to download structure (HTTP {response.status_code})"
                            )
                    except Exception as e:
                        st.error(f"Error fetching AlphaFold structure: {str(e)}")
                except Exception as e:
                    st.error(f"Could not load AlphaFold structure: {str(e)}")

        if (pd.isna(pdb_value) or not pdb_value) and (
            pd.isna(alphafold_value) or not alphafold_value
        ):
            st.info("No 3D structures available for this protein.")

    with chembl_tab:
        st.subheader("ChEMBL Data")
        st.info("ChEMBL chemical and bioactivity data will be displayed here.")
