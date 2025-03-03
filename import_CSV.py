import pandas as pd

list_field_uniprot = [
        "Entry",
        "Entry Name",
        "Protein names",
        "Gene Names",
        "Organism",
        "Sequence",
        "Length",
        "Mass",
        "Tissue specificity",
        "Subcellular location [CC]"
    ]

list_field_drugbank = ["DrugBank ID",
                       "Name",
                       "Type","Groups",
                       "Description",
                       "Synonyms",
                       "Absorption",
                       "Protein Binding",
                       "Food Interactions",
                       "Affected Organisms",
                       "Chemical Formula",
                       "Molecular Weight",
                       "IUPAC Name",
                       "CAS Number",
                       "InChIKey",
                       "UNII",
                       "Patents",
                       "Spectra"]

df_uniprot = pd.read_csv("uniprot.csv")
df_drugbank = pd.read_csv("drugbank.csv")

def get_uniprot_drugbank():
    """
    Return indices of rows in df_drugbank that match DrugBank IDs found in df_uniprot,
    preserving the order of data in uniprot.csv
    """
    # Initialize a list to store drugbank indices for each row in uniprot
    # Use None for rows that don't have DrugBank entries
    result = [None] * len(df_uniprot)
    
    # Find rows in df_uniprot that have DrugBank entries
    request = (~pd.isna(df_uniprot["DrugBank"])) & (df_uniprot["DrugBank"] != "")
    
    # Get the list of indices with DrugBank entries
    uniprot_indices = df_uniprot[request].index.tolist()
    
    # Process only rows that have DrugBank entries
    for idx in uniprot_indices:
        # Extract DrugBank IDs for this uniprot entry
        drugbank_ids = parse_drugbank_ids(df_uniprot.loc[idx, "DrugBank"])
        drugbank_ids = list(set(drugbank_ids))  # Remove duplicates
        matched_indices = []
        for db_id in drugbank_ids:
            mask = df_drugbank["DrugBank ID"] == db_id
            if mask.any():
                matched_indices.extend(df_drugbank[mask].index.tolist())
        
        # Store the matched indices at the corresponding position
        result[idx] = matched_indices
    
    # Filter out None entries if you only want results for rows with matches
    result = [indices for indices in result if indices is not None]
    
    return result

def parse_drugbank_ids(text):
    """
    Parse a text containing DrugBank IDs formatted as "DBXXXXX; Name." and return a list of DrugBank IDs.
    """
    if pd.isna(text) or not text:
        return []
    
    # Split by quotes and semicolons
    parts = text.split('"')
    ids = []
    
    for part in parts:
        part = part.strip()
        if part.startswith('DB'):
            # Extract the part before the semicolon
            db_id = part.split(';')[0].strip()
            ids.append(db_id)
            
    return ids

def extract_filters_uniprot():
    # Get your original filters first (your existing code)
    filters = {column:df_uniprot[column].unique().tolist() for column in list_field_uniprot}
    
    # Special handling for Gene Names
    if "Gene Names" in filters:
        # Split the combined gene names and process them
        all_genes = []
        for gene_group in filters["Gene Names"]:
            if pd.notna(gene_group) and gene_group:
                # Split by space and ensure capitalization
                genes = [gene.strip().upper() for gene in gene_group.split() if gene.strip()]
                all_genes.extend(genes)
        
        # Remove duplicates and sort
        filters["Gene Names"] = sorted(list(set(all_genes)))
    
    return filters

def get_attribute_values_uniprot(data,field): #Renvoie la liste des valeurs pour un attribut donné
    return data.get(field)

def filter_results_uniprot(dic): 
    '''dic contient les fields en clés et les valeurs sont des listes de valeurs correspondant 
    à union des field=value
    On renvoie une liste d'indices (ligne 2 du csv correspond à 0)'''
    if len(dic.keys())==0:
        return df_uniprot.index.tolist()
    else:
        request=pd.Series([True] * len(df_uniprot))
        
        # Handle gene names separately
        gene_names_filter = None
        if "Gene Names" in dic and dic["Gene Names"]:
            selected_genes = dic["Gene Names"]
            gene_names_filter = pd.Series([False] * len(df_uniprot))
            
            # For each row in the data
            for i, gene_group in enumerate(df_uniprot["Gene Names"]):
                if pd.notna(gene_group):
                    # Convert to string in case it's not already
                    gene_string = str(gene_group).upper()
                    # Check if any selected gene is in this entry's gene group
                    if any(gene.upper() in gene_string for gene in selected_genes):
                        gene_names_filter.iloc[i] = True
        
        # Handle sequence search separately
        sequence_filter = None
        if "Sequence" in dic and dic["Sequence"]:
            sequence_query = dic["Sequence"].upper()
            sequence_filter = pd.Series([False] * len(df_uniprot))
            
            # For each row in the data
            for i, sequence in enumerate(df_uniprot["Sequence"]):
                if pd.notna(sequence):
                    # Convert to string and clean up whitespace
                    sequence_str = str(sequence).upper().replace(" ", "")
                    # Check if the query is in this sequence
                    if sequence_query in sequence_str:
                        sequence_filter.iloc[i] = True
        
        # Process all other filters normally
        for field in dic.keys():
            # Skip Gene Names and Sequence as we're handling them separately
            if field == "Gene Names" or field == "Sequence":
                continue
                
            if isinstance(dic[field], tuple):
                request &= (df_uniprot[field] >= dic[field][0]) & (df_uniprot[field] <= dic[field][1])
            else:
                request_or = pd.Series([False] * len(df_uniprot))
                if len(dic[field])!=0:
                    for value in dic[field]:
                        request_or |= (df_uniprot[field] == value)
                    request &= request_or
        
        # Combine the special filters with other filters if they exist
        if gene_names_filter is not None:
            request &= gene_names_filter
            
        if sequence_filter is not None:
            request &= sequence_filter
            
        filtered_df = df_uniprot.loc[request]
        return filtered_df.index.tolist()


def get_values_for_rows_uniprot(list_index, list_fields):#Renvoie un dictionnaire où les clés sont les attributs de list_fields
    #et où les valeurs sont des listes où chaque élément correspond à la valeur de l'attribut pour une ligne 
    dic = {}
    for field in list_fields:
        dic[field] = df_uniprot.loc[list_index,field].tolist()
    return dic

def extract_filters_drugbank():
    # Get your original filters first
    filters = {column:df_drugbank[column].unique().tolist() for column in list_field_drugbank}
    
    # Convert numeric fields to proper numbers
    for key in ["Absorption", "Protein Binding", "Molecular Weight"]:
        if key in filters:
            numeric_values = []
            for value in filters[key]:
                if pd.notna(value):
                    if key in ["Absorption", "Protein Binding"]:
                        # Extract percentages using regex
                        import re
                        matches = re.findall(r'(\d+(?:\.\d+)?)%', str(value))
                        if matches:
                            numeric_values.extend([float(match) for match in matches])
                    else:  # Molecular Weight
                        try:
                            # Try to convert to float directly
                            numeric_values.append(float(value))
                        except (ValueError, TypeError):
                            pass
            
            # Replace the original values with numeric ones
            if numeric_values:
                filters[key] = numeric_values
            else:
                # If no numeric values were found, provide defaults
                if key in ["Absorption", "Protein Binding"]:
                    filters[key] = [0.0, 100.0]  # Default percentage range
                else:  # Molecular Weight
                    filters[key] = [100.0, 1000.0]  # Default weight range
    
    return filters

def get_attribute_values_drugbank(data,field): #Renvoie la liste des valeurs pour un attribut donné
    return data.get(field)

def filter_results_drugbank(dic):
    '''dic contient les fields en clés et les valeurs sont des listes de valeurs correspondant 
    à union des field=value
    On renvoie une liste d'indices (ligne 2 du csv correspond à 0)'''
    if len(dic.keys())==0:
        return df_drugbank.index.tolist()
    else:
        request=pd.Series([True] * len(df_drugbank))
        
        # Process all filters
        for field in dic.keys():
            # Skip empty filters
            if not dic[field]:
                continue
                
            if isinstance(dic[field], tuple):
                min_val, max_val = dic[field]
                
                # Handle special fields with percentage extraction
                if field in ["Absorption", "Protein Binding"]:
                    field_request = pd.Series([False] * len(df_drugbank))
                    
                    for i, value in enumerate(df_drugbank[field]):
                        if pd.notna(value):
                            # Extract percentages using regex
                            import re
                            matches = re.findall(r'(\d+(?:\.\d+)?)%', str(value))
                            if matches:
                                percentages = [float(match) for match in matches]
                                # If any percentage is in range, include this entry
                                if any(min_val <= p <= max_val for p in percentages):
                                    field_request.iloc[i] = True
                    
                    request &= field_request
                    
                # Handle normal numeric fields like Molecular Weight
                else:
                    # Convert column to numeric, forcing non-convertible values to NaN
                    numeric_values = pd.to_numeric(df_drugbank[field], errors='coerce')
                    # Create a mask for valid rows that meet the criteria
                    valid_rows = (numeric_values >= min_val) & (numeric_values <= max_val)
                    # Fill NaN values with False in the mask
                    valid_rows = valid_rows.fillna(False)
                    request &= valid_rows
            else:
                request_or = pd.Series([False] * len(df_drugbank))
                for value in dic[field]:
                    request_or |= (df_drugbank[field] == value)
                request &= request_or
        
        filtered_df = df_drugbank.loc[request]
        return filtered_df.index.tolist()

def get_values_for_rows_drugbank(list_index_uniprot,list_index,list_fields):#Renvoie un dictionnaire où les clés sont les attributs de list_fields
    #et où les valeurs sont des listes où chaque élément correspond à la valeur de l'attribut pour une ligne

    if 9 not in list_index_uniprot and 10 not in list_index_uniprot and 12 not in list_index_uniprot:
        return []
    else:

        list_index_drugbank_uniprot = get_uniprot_drugbank()
        list_dic = []
        for list_index_drugbank in list_index_drugbank_uniprot:
            dic = {}
            for field in list_fields:
                dic[field] = df_drugbank.loc[list(set(list_index_drugbank)&set(list_index)),field].tolist()
                list_dic.append(dic)
        return list_dic
    