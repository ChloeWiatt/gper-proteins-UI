import streamlit as st
from import_CSV import *
import py3Dmol
import re
import pandas as pd

# Extract filters and initialize filter dictionaries
filters_uniprot = extract_filters_uniprot()
filters_drugbank = {}
filters_pdb = {}
filters_chembl = {}

# Define fields to display from Uniprot
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
    "Subcellular location [CC]",
    "Function [CC]",
    "Involvement in disease",
    "Mutagenesis",
    "PubMed ID",
    "DOI ID",
    "PDB",
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
            "has_location": "Subcellular location",
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
            "📍 Location": ["Tissue specificity", "Subcellular location [CC]"],
        }

        for expander, keys in expanders.items():
            with st.expander(expander):
                for key in keys:
                    if key == "Mass":
                        st.markdown(f"**{key} (Da)**")
                    else:
                        st.markdown(f"**{key}**")
                    values = filters_uniprot[key]
                    if key in ["Length", "Mass"]:
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
        drugbank_choices = []
        for key, values in filters_drugbank.items():
            with st.expander(key):
                drugbank_choices.append(
                    st.multiselect(
                        f"Select {key}", options=values, label_visibility="collapsed"
                    )
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
filtered_results = get_values_for_rows_uniprot(
    filter_results_uniprot(uniprot_choices), uniprot_selections
)
# Universal search bar
search_query = st.text_input(
    "🔍 Search by keyword, sequence or formula",
    help="Ex: 'GPER1 human' or 'C28H34N6O4S'",
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
                for key, value in filtered_results.items():
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

    st.title(f"Detailed View: {filtered_results['Entry Name'][protein_idx]}")

    # Create tabs for different databases
    uniprot_tab, drugbank_tab, pdb_tab, chembl_tab = st.tabs(
        ["🧬 UniProt", "💊 DrugBank", "🔬 PDB", "🧪 ChEMBL"]
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
                            pubmed_html_links.append(f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}" target="_blank">{pmid}</a>')
                        
                        pubmed_text = ", ".join(pubmed_html_links) if pubmed_html_links else "N/A"

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
                        st.write("**Mutations:**")
                        st.markdown(
                            df.to_html(escape=False),
                            unsafe_allow_html=True
                        )
                elif field == "Mass":
                    st.markdown(f"**{field}:** {value} Da")
                elif field =="PDB":
                    continue
                else:
                    st.markdown(f"**{field}:** {value}")
                st.divider()  # Add a divider between fields

    with drugbank_tab:
        st.subheader("DrugBank Information")
        st.info("DrugBank data will be displayed here.")

    with pdb_tab:
        st.subheader("PDB Structures")
        if pd.isna(value) :
            st.info("No PDB structures available for this protein.")
        else:
            pdb_id = value.split(";")[0].strip('"')
            view = py3Dmol.view(query=f"pdb:{pdb_id}")
            view.setStyle({"cartoon": {"color": "spectrum"}})
            st.components.v1.html(view._make_html(), height=500)
    with chembl_tab:
        st.subheader("ChEMBL Data")
        st.info("ChEMBL chemical and bioactivity data will be displayed here.")
