import json
import pandas as pd
from tqdm import tqdm
from chembl_webresource_client.new_client import new_client

# Define fields for ChEMBL data
list_field_chembl = [
    "molecule_chembl_id",
    "pref_name",
    "molecule_type", 
    "max_phase",
    "first_approval",
    "oral",
    "parenteral",
    "topical",
    "black_box_warning",
    "molecule_properties.alogp",
    "molecule_properties.full_mwt",
    "molecule_properties.num_ro5_violations"
]

def extract_chembl_ids_from_uniprot(df_uniprot, chembl_col_index=139):
    """Extract ChEMBL IDs from the uniprot.csv file
    
    Parameters:
    - df_uniprot: DataFrame containing UniProt data
    - chembl_col_index: Index of the column containing ChEMBL IDs (default: 139)
    """
    # Check if column exists and get its name
    if chembl_col_index < len(df_uniprot.columns):
        chembl_col = df_uniprot.columns[chembl_col_index]
        print(f"Looking for ChEMBL IDs in column: '{chembl_col}'")
        
        # Print a few sample values
        sample_values = [v for v in df_uniprot[chembl_col].dropna().head(3) if isinstance(v, str)]
        print("Sample values from this column:")
        for v in sample_values:
            print(f"  {v}")
            
        # Extract IDs and remove semicolons
        chembl_ids = []
        for value in df_uniprot[chembl_col]:
            if pd.notna(value) and isinstance(value, str):
                # Extract IDs and clean them (remove semicolons)
                ids = [id.strip().rstrip(';') for id in value.split() if id.strip().startswith('CHEMBL')]
                chembl_ids.extend(ids)
        
        return list(set(chembl_ids))
    else:
        print(f"Warning: Column index {chembl_col_index+1} doesn't exist in uniprot.csv")
        return []

def identify_chembl_id_type(chembl_id):
    """Identify if a ChEMBL ID refers to a target or a molecule"""
    molecule = new_client.molecule
    target = new_client.target
    
    # Try as target
    target_data = target.filter(target_chembl_id=chembl_id)
    if target_data:
        return "target", target_data[0]
    
    # Try as molecule
    mol_data = molecule.filter(molecule_chembl_id=chembl_id)
    if mol_data:
        return "molecule", mol_data[0]
    
    # Not found
    return "unknown", None

def analyze_uniprot_chembl_ids(df_uniprot=None):
    """Analyze the ChEMBL IDs from UniProt data"""
    if df_uniprot is None:
        try:
            df_uniprot = pd.read_csv("uniprot.csv")
        except Exception as e:
            print(f"Error loading uniprot.csv: {str(e)}")
            return [], [], []
    
    uniprot_ids = extract_chembl_ids_from_uniprot(df_uniprot)
    
    targets = []
    molecules = []
    unknown = []
    
    for chembl_id in tqdm(uniprot_ids, desc="Analyzing ChEMBL IDs"):
        id_type, data = identify_chembl_id_type(chembl_id)
        
        if id_type == "target":
            name = data.get("pref_name", "Unknown")
            targets.append((chembl_id, name))
        elif id_type == "molecule":
            name = data.get("pref_name", "Unknown compound")
            molecules.append((chembl_id, name))
        else:
            unknown.append(chembl_id)
    
    print(f"\nFound {len(targets)} targets:")
    for target_id, name in targets:
        print(f"  - {target_id}: {name}")
    
    print(f"\nFound {len(molecules)} molecules:")
    for mol_id, name in molecules:
        print(f"  - {mol_id}: {name}")
    
    print(f"\nFound {len(unknown)} unknown IDs:")
    for id in unknown:
        print(f"  - {id}")
    
    return targets, molecules, unknown

def build_focused_gper_database(force_update=False, activity_threshold=None):
    """Build a focused database with GPER compounds
    
    Parameters:
    - force_update: Whether to rebuild the database from scratch
    - activity_threshold: Optional maximum activity value (nM) to include
    """
    cache_file = "gper_compounds.json"
    
    # Try loading from cache if not forced to update
    if not force_update:
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                print(f"Loaded {len(data['molecules'])} GPER compounds from cache")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            print("Building new GPER compounds database...")
    
    # Initialize result containers
    result = {
        "molecules": {},  # Store molecule data
        "targets": {},    # Store target data
        "activities": {}  # Store molecule-target activity data  
    }
    
    # Initialize ChEMBL client
    molecule = new_client.molecule
    target = new_client.target
    activity = new_client.activity
    
    # Search for GPER targets
    print("Looking for GPER targets...")
    target_results = target.search('GPER OR "G-protein coupled estrogen receptor"')
    
    # Filter for GPER targets
    gper_targets = {}
    for t in target_results:
        if 'target_chembl_id' in t and 'pref_name' in t:
            name = t['pref_name'].lower()
            if 'gper' in name or 'g-protein coupled estrogen receptor' in name:
                target_id = t['target_chembl_id']
                gper_targets[target_id] = t
                result["targets"][target_id] = t
                print(f"Found GPER target: {target_id} ({t.get('pref_name', 'Unknown')})")
    
    # For each GPER target, get compounds
    print(f"\nFetching compounds for {len(gper_targets)} GPER targets...")
    
    for target_id, target_info in gper_targets.items():
        print(f"Getting activities for {target_id} ({target_info.get('pref_name', 'Unknown')})")
        
        try:
            # Get activities for this target
            activities_data = activity.filter(target_chembl_id=target_id)
            print(f"  Found {len(activities_data)} activities")
            
            # Filter activities if needed
            filtered_activities = []
            for act in activities_data:
                include = True
                
                # Filter by activity threshold if specified
                if activity_threshold is not None and 'standard_value' in act and 'standard_units' in act and act['standard_units'] == 'nM':
                    try:
                        if float(act['standard_value']) > activity_threshold:
                            include = False
                    except (ValueError, TypeError):
                        pass
                
                if include and 'molecule_chembl_id' in act:
                    filtered_activities.append(act)
                    key = f"{act['molecule_chembl_id']}_{target_id}"
                    result["activities"][key] = act
            
            # Report activities
            print(f"  Using {len(filtered_activities)} activities after filtering")
            
            # Get molecule IDs
            molecule_ids = set()
            for act in filtered_activities:
                molecule_ids.add(act['molecule_chembl_id'])
            
            # Fetch molecule data in batches
            if molecule_ids:
                print(f"  Fetching {len(molecule_ids)} molecules")
                for i in range(0, len(molecule_ids), 50):
                    batch = list(molecule_ids)[i:i+50]
                    mol_data = molecule.filter(molecule_chembl_id__in=batch)
                    for mol in mol_data:
                        mol_id = mol.get('molecule_chembl_id')
                        if mol_id:
                            result["molecules"][mol_id] = mol
                    print(f"    Fetched batch {i//50 + 1}/{(len(molecule_ids) + 49)//50}")
            
        except Exception as e:
            print(f"  Error processing {target_id}: {str(e)}")
    
    # Save the data
    with open(cache_file, "w") as f:
        json.dump(result, f)
    
    print(f"\nSaved GPER database with:")
    print(f"  - {len(result['molecules'])} molecules") 
    print(f"  - {len(result['targets'])} targets")
    print(f"  - {len(result['activities'])} activities")
    
    return result

def extract_filters_chembl(data=None):
    """Extract filter options for ChEMBL data
    
    Parameters:
    - data: Optional pre-loaded database (will load from cache if not provided)
    """
    # Get data if not provided
    if data is None:
        data = build_focused_gper_database()
    
    filters = {}
    
    # Extract unique values for each field
    for field in list_field_chembl:
        values = []
        
        for mol_data in data["molecules"].values():
            # Handle nested fields
            if '.' in field:
                parent, child = field.split('.')
                if parent in mol_data and mol_data[parent] and child in mol_data[parent]:
                    values.append(mol_data[parent][child])
            elif field in mol_data:
                values.append(mol_data[field])
        
        # Remove None values and duplicates
        values = [v for v in values if v is not None]
        if len(values) > 0:
            if all(isinstance(v, (int, float)) for v in values):
                # For numeric fields, store min/max
                filters[field] = (min(values), max(values))
            else:
                # For categorical fields, store unique values
                filters[field] = sorted(list(set(str(v) for v in values)))
    
    return filters

def filter_results_chembl(filter_choices, data=None):
    """Filter ChEMBL results based on selected filters
    
    Parameters:
    - filter_choices: Dictionary of filter criteria
    - data: Optional pre-loaded database (will load from cache if not provided)
    """
    # Get data if not provided
    if data is None:
        data = build_focused_gper_database()
    
    # Default to all IDs if no filters
    if not filter_choices:
        return list(data["molecules"].keys())
    
    matching_ids = []
    
    for chembl_id, mol_data in data["molecules"].items():
        match = True
        
        for field, values in filter_choices.items():
            if not values:  # Skip empty filters
                continue
            
            # Get the field value (handle nested fields)
            field_value = None
            if '.' in field:
                parent, child = field.split('.')
                if parent in mol_data and mol_data[parent] and child in mol_data[parent]:
                    field_value = mol_data[parent][child]
            else:
                field_value = mol_data.get(field)
            
            if field_value is None:
                match = False
                break
            
            # Check if value matches filter
            if isinstance(values, tuple):  # Range filter
                try:
                    if not (float(field_value) >= values[0] and float(field_value) <= values[1]):
                        match = False
                        break
                except (ValueError, TypeError):
                    match = False
                    break
            else:  # List of values
                if str(field_value) not in values:
                    match = False
                    break
        
        if match:
            matching_ids.append(chembl_id)
    
    return matching_ids

def get_values_for_rows_chembl(chembl_ids, fields, data=None):
    """Get values for specific fields for the given ChEMBL IDs
    
    Parameters:
    - chembl_ids: List of ChEMBL IDs to retrieve data for
    - fields: List of fields to retrieve
    - data: Optional pre-loaded database (will load from cache if not provided)
    """
    # Get data if not provided
    if data is None:
        data = build_focused_gper_database()
    
    result = {field: [] for field in fields}
    
    for chembl_id in chembl_ids:
        if chembl_id in data["molecules"]:
            mol_data = data["molecules"][chembl_id]
            
            for field in fields:
                # Handle nested fields
                if '.' in field:
                    parent, child = field.split('.')
                    if parent in mol_data and mol_data[parent] and child in mol_data[parent]:
                        result[field].append(mol_data[parent][child])
                    else:
                        result[field].append(None)
                else:
                    result[field].append(mol_data.get(field))
        else:
            # If ID not found, add None for all fields
            for field in fields:
                result[field].append(None)
    
    return result

def create_target_csv(target_ids=None):
    """Create a CSV file with information about specific ChEMBL targets
    
    Parameters:
    - target_ids: List of ChEMBL target IDs to include
    """
    if target_ids is None:
        target_ids = ["CHEMBL3309103", "CHEMBL213", "CHEMBL2107", "CHEMBL5872"]
    
    # Clean the IDs (remove any semicolons)
    target_ids = [tid.rstrip(";") for tid in target_ids]
    
    print(f"Creating CSV for {len(target_ids)} targets...")
    
    # Initialize the client
    target = new_client.target
    
    # Fetch data for each target
    target_data = []
    for tid in target_ids:
        try:
            data = target.filter(target_chembl_id=tid)
            if data:
                # Extract key information
                t = data[0]
                target_data.append({
                    "target_chembl_id": t.get("target_chembl_id", ""),
                    "pref_name": t.get("pref_name", ""),
                    "organism": t.get("organism", ""),
                    "target_type": t.get("target_type", ""),
                    "tax_id": t.get("tax_id", ""),
                    "species_group_flag": t.get("species_group_flag", ""),
                    "description": t.get("description", "")
                })
                print(f"Added data for {tid}: {t.get('pref_name', 'Unknown')}")
            else:
                print(f"No data found for target {tid}")
        except Exception as e:
            print(f"Error fetching target {tid}: {str(e)}")
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(target_data)
    csv_path = "chembl_targets.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved target data to {csv_path}")
    return csv_path

def create_gper_compounds_csv(num_compounds=50, activity_threshold=None):
    """Create a CSV file with top GPER-related compounds
    
    Parameters:
    - num_compounds: Number of top compounds to include
    - activity_threshold: Optional maximum activity value in nM to filter by
    """
    print(f"Creating CSV for top {num_compounds} GPER compounds...")
    
    # Build the focused database if needed
    result = build_focused_gper_database(force_update=False, 
                                         activity_threshold=activity_threshold)
    
    # Extract all compounds with activity against GPER targets
    compounds_with_activity = []
    
    # First determine which targets are GPER-related
    gper_target_ids = []
    for target_id, target_info in result["targets"].items():
        name = target_info.get("pref_name", "").lower()
        if "gper" in name or "g-protein coupled estrogen receptor" in name:
            gper_target_ids.append(target_id)
    
    print(f"Found {len(gper_target_ids)} GPER targets")
    
    # Collect all activities for these targets
    all_gper_activities = []
    for key, activity_data in result["activities"].items():
        target_id = activity_data.get("target_chembl_id")
        if target_id in gper_target_ids:
            try:
                # Check if it has valid activity data
                if ('standard_type' in activity_data and 
                    activity_data['standard_type'] in ['IC50', 'Ki', 'Kd', 'EC50', 'Potency'] and
                    'standard_value' in activity_data and
                    'molecule_chembl_id' in activity_data and
                    'standard_units' in activity_data):
                    value = float(activity_data['standard_value'])
                    mol_id = activity_data['molecule_chembl_id']
                    if mol_id in result["molecules"]:
                        all_gper_activities.append((value, mol_id, target_id, activity_data))
            except (ValueError, TypeError):
                pass
    
    # Sort by activity value (lower is better)
    all_gper_activities.sort()
    
    # Take the top compounds
    top_activities = all_gper_activities[:num_compounds]
    
    # Prepare data for CSV
    compound_data = []
    for value, mol_id, target_id, activity_data in top_activities:
        if mol_id in result["molecules"]:
            molecule = result["molecules"][mol_id]
            
            # Get structures if available
            smiles = None
            if 'molecule_structures' in molecule and molecule['molecule_structures']:
                smiles = molecule['molecule_structures'].get('canonical_smiles')
            
            # Get properties if available
            mw = None
            logp = None
            ro5_violations = None
            if 'molecule_properties' in molecule and molecule['molecule_properties']:
                props = molecule['molecule_properties']
                mw = props.get('full_mwt')
                logp = props.get('alogp')
                ro5_violations = props.get('num_ro5_violations')
            
            # Get target information
            target_name = result["targets"].get(target_id, {}).get('pref_name', 'Unknown')
            
            # Compile row data
            row_data = {
                "molecule_chembl_id": mol_id,
                "pref_name": molecule.get('pref_name'),
                "smiles": smiles,
                "activity_type": activity_data.get('standard_type'),
                "activity_value": value,
                "activity_units": activity_data.get('standard_units'),
                "target_chembl_id": target_id,
                "target_name": target_name,
                "molecular_weight": mw,
                "logp": logp,
                "ro5_violations": ro5_violations,
                "max_phase": molecule.get('max_phase'),
                "first_approval": molecule.get('first_approval'),
                "molecule_type": molecule.get('molecule_type')
            }
            compound_data.append(row_data)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(compound_data)
    csv_path = "top_gper_compounds.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(df)} compounds to {csv_path}")
    return csv_path

def create_enhanced_target_csv(target_ids=None):
    """Create an enhanced CSV file with detailed information about specific ChEMBL targets
    
    Parameters:
    - target_ids: List of ChEMBL target IDs to include
    """
    if target_ids is None:
        target_ids = ["CHEMBL3309103", "CHEMBL213", "CHEMBL2107", "CHEMBL5872"]
    
    # Clean the IDs (remove any semicolons)
    target_ids = [tid.rstrip(";") for tid in target_ids]
    
    print(f"Creating enhanced CSV for {len(target_ids)} targets...")
    
    # Initialize the clients
    target = new_client.target
    activity = new_client.activity
    molecule = new_client.molecule
    mechanism = new_client.mechanism
    
    # Fetch detailed data for each target
    target_data = []
    for tid in target_ids:
        try:
            print(f"Processing target {tid}...")
            t_data = target.filter(target_chembl_id=tid)
            if t_data:
                t = t_data[0]
                
                # Get basic target info
                target_info = {
                    "target_chembl_id": t.get("target_chembl_id", ""),
                    "pref_name": t.get("pref_name", ""),
                    "organism": t.get("organism", ""),
                    "target_type": t.get("target_type", ""),
                }
                
                # Get protein classification
                classification = []
                if "target_components" in t:
                    for component in t["target_components"]:
                        if "target_component_xrefs" in component:
                            for xref in component["target_component_xrefs"]:
                                if xref.get("xref_src") == "UniProt":
                                    target_info["uniprot_id"] = xref.get("xref_id", "")
                                    
                        if "protein_classifications" in component:
                            for pc in component["protein_classifications"]:
                                classification.append(f"{pc.get('protein_classification_level1', '')} - {pc.get('protein_classification_level2', '')}")
                
                target_info["protein_classification"] = "; ".join(set(classification))
                
                # Get activity statistics
                print(f"  Getting activities...")
                acts = activity.filter(target_chembl_id=tid)
                target_info["activity_count"] = len(acts)
                
                # Get activity types and values
                activity_types = set()
                activity_values = []
                
                for act in acts:
                    if "standard_type" in act:
                        activity_types.add(act["standard_type"])
                    
                    if "standard_value" in act and "standard_units" in act and act["standard_units"] == "nM":
                        try:
                            activity_values.append(float(act["standard_value"]))
                        except (ValueError, TypeError):
                            pass
                
                target_info["activity_types"] = ", ".join(sorted(activity_types))
                
                # Calculate activity statistics if available
                if activity_values:
                    target_info["min_activity_nM"] = min(activity_values)
                    target_info["max_activity_nM"] = max(activity_values)
                    target_info["median_activity_nM"] = sorted(activity_values)[len(activity_values)//2]
                
                # Get drug mechanism info
                print(f"  Getting drug mechanisms...")
                mechs = mechanism.filter(target_chembl_id=tid)
                target_info["known_drug_mechanisms"] = len(mechs)
                
                # Get drug names for this target
                drug_names = []
                for mech in mechs:
                    if "molecule_chembl_id" in mech:
                        mol_id = mech["molecule_chembl_id"]
                        mol_data = molecule.filter(molecule_chembl_id=mol_id)
                        if mol_data and "pref_name" in mol_data[0] and mol_data[0]["pref_name"]:
                            drug_names.append(mol_data[0]["pref_name"])
                
                target_info["known_drugs"] = "; ".join(drug_names[:5])  # Limit to top 5
                target_info["total_known_drugs"] = len(drug_names)
                
                # Get citation count (publication data)
                if "cross_references" in t:
                    for ref in t["cross_references"]:
                        if ref.get("xref_src") == "PubMed":
                            target_info["pubmed_id"] = ref.get("xref_id", "")
                
                # Add to results
                target_data.append(target_info)
                print(f"  Completed {tid}: {t.get('pref_name', 'Unknown')}")
            else:
                print(f"No data found for target {tid}")
                
        except Exception as e:
            print(f"Error fetching target {tid}: {str(e)}")
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(target_data)
    csv_path = "chembl_targets_enhanced.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved enhanced target data to {csv_path}")
    return csv_path

if __name__ == "__main__":

    print("ChEMBL Data Processing Tool")
    print("==========================\n")
    
    print("1. Analyzing ChEMBL IDs from UniProt...")
    try:
        df_uniprot = pd.read_csv("uniprot.csv")
        targets, molecules, unknown = analyze_uniprot_chembl_ids(df_uniprot)
    except Exception as e:
        print(f"Error analyzing UniProt data: {str(e)}")
    
    print("\n2. Creating enhanced CSV for specific targets...")
    enhanced_target_csv = create_enhanced_target_csv(["CHEMBL3309103", "CHEMBL213", "CHEMBL2107", "CHEMBL5872"])
    
    print("\n3. Creating CSV for top 50 GPER compounds...")
    compounds_csv = create_gper_compounds_csv(num_compounds=50)
    
    print("\nCSV files generated:")
    print(f"1. Enhanced target information: {enhanced_target_csv}")
    print(f"2. Top GPER compounds: {compounds_csv}")