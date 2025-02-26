import pandas as pd

list_field = [
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

df = pd.read_csv("uniprot.csv")

def extract_filters(): #Renvoie un dictionnaire ou les clés 
    #sont les élements de lists_field et les valeurs les listes sans redondance 
    #contenant les valeurs possibles de l'attribut
    data={column:df[column].unique().tolist() for column in list_field}
    return data

def get_attribute_values(data,field): #Renvoie la liste des valeurs pour un attribut donné
    return data.get(field)

def filter_results(fields,field_values): #Renvoie la liste des indexs de lignes de df pour chaque 
    #ligne qui matche field==field_value
    #La première ligne contenant des données correspont à l'index 0
    request=True
    for field,value in zip(fields, field_values):
        request &= (df[field]==value)
    filtered_df =df.loc[request]
    return filtered_df.index.tolist()

def get_values_for_rows(list_index, list_fields):#Renvoie un dictionnaire où les clés sont les attributs de list_fields
    #et où les valeurs sont des listes où chaque élément correspond à la valeur de l'attribut pour une ligne 
    dic = {}
    for field in list_fields:
        dic[field] = df.loc[list_index,field].tolist()
    return dic
