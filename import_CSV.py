import pandas as pd

list_field = [
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
        "DOI ID"
    ]

df = pd.read_csv("uniprot.csv")

def generate_data(): #Renvoie un dictionnaire ou les clés 
    #sont les élements de lists_field et les valeurs les listes sans redondance 
    #contenant les valeurs possibles de l'attribut
    data={column:df[column].unique().tolist() for column in list_field}
    return data

def get_data(data,field): #Renvoie la liste des valeurs pour un attribut donné
    return data.get(field)

def filter(field,field_value): #Renvoie la liste des indexs de lignes de df pour chaque 
    #ligne qui matche field==field_value

    #La première ligne contenant des données correspont à l'index 0
    filtered_df = df.loc[df[field] == field_value]
    return filtered_df.index.tolist()
