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
        "Subcellular location",
        "Function [CC]",
        "Involvement in disease",
        "Mutagenesis",
        "PubMed ID",
        "DOI ID"
    ]

def import_csv(csv_file):
    df = pd.read_csv(csv_file)
    return df

def generate_data(df): #Renvoie un dictionnaire ou les clés 
    #sont les attributs et les valeurs les listes sans redondance 
    #contenant les valeurs possibles de l'attribut
    data = {}
    for column in df.columns:
        data_column = df[column].unique().tolist()
        data[column] = data_column
    return data

def get_data(data,field): #Renvoie la liste des valeurs pour un attribut donné
    return data.get(field, None)

def filter(df,field,field_value): #Renvoie la liste des indexs de lignes de df pour chaque 
    #ligne qui matche field==field_value

    #La première ligne contenant des données correspont à l'index 0
    filtered_df = df.loc[df[field] == field_value]
    return filtered_df.index.tolist()




