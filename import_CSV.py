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

df_uniprot = pd.read_csv("uniprot.csv")

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
        
        # Process all other filters normally
        for field in dic.keys():
            # Skip Gene Names as we're handling it separately
            if field == "Gene Names":
                continue
                
            if isinstance(dic[field], tuple):
                request &= (df_uniprot[field] >= dic[field][0]) & (df_uniprot[field] <= dic[field][1])
            else:
                request_or = pd.Series([False] * len(df_uniprot))
                if len(dic[field])!=0:
                    for value in dic[field]:
                        request_or |= (df_uniprot[field] == value)
                    request &= request_or
        
        # Combine the gene names filter with other filters if it exists
        if gene_names_filter is not None:
            request &= gene_names_filter
            
        filtered_df = df_uniprot.loc[request]
        return filtered_df.index.tolist()


def get_values_for_rows_uniprot(list_index, list_fields):#Renvoie un dictionnaire où les clés sont les attributs de list_fields
    #et où les valeurs sont des listes où chaque élément correspond à la valeur de l'attribut pour une ligne 
    dic = {}
    for field in list_fields:
        dic[field] = df_uniprot.loc[list_index,field].tolist()
    return dic