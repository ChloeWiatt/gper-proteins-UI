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

def extract_filters_uniprot(): #Renvoie un dictionnaire ou les clés 
    #sont les élements de lists_field et les valeurs les listes sans redondance 
    #contenant les valeurs possibles de l'attribut
    data={column:df_uniprot[column].unique().tolist() for column in list_field_uniprot}
    return data

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
        for field in dic.keys():
            if isinstance(dic[field],tuple):
                request &= (df_uniprot[field] >= dic[field][0]) & (df_uniprot[field] <= dic[field][1])
            else:
                request_or = pd.Series([False] * len(df_uniprot))
                if len(dic[field])!=0:
                    for value in dic[field]:
                        request_or |= (df_uniprot[field] == value)
                    request &= request_or
        filtered_df =df_uniprot.loc[request]
        return filtered_df.index.tolist()


def get_values_for_rows_uniprot(list_index, list_fields):#Renvoie un dictionnaire où les clés sont les attributs de list_fields
    #et où les valeurs sont des listes où chaque élément correspond à la valeur de l'attribut pour une ligne 
    dic = {}
    for field in list_fields:
        dic[field] = df_uniprot.loc[list_index,field].tolist()
    return dic