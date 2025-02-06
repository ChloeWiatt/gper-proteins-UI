import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def build_uniprot_query(params):
    """
    Construit une chaîne de requête pour l'API Uniprot en fonction des filtres fournis.
    Utilise "gene:" pour le nom du gène (le champ correct dans la requête).
    """
    query_parts = []
    if params.get("gene_name"):
        # Utilisation de "gene:" pour filtrer sur le nom du gène
        query_parts.append(f'gene:{params["gene_name"]}')
    if params.get("organism"):
        # La recherche par organisme se fait en mettant le nom entre guillemets
        query_parts.append(f'organism:"{params["organism"]}"')
    if params.get("ptm"):
        # Recherche dans les annotations textuelles concernant les modifications post-traductionnelles
        query_parts.append(f'annotation:(ptm {params["ptm"]})')
    if params.get("pdb"):
        # Recherche dans les références PDB
        query_parts.append(f'xref_pdb:{params["pdb"]}')
    
    return " AND ".join(query_parts) if query_parts else ""

def get_uniprot_data(query):
    """
    Interroge l'API Uniprot pour récupérer les données protéiques en JSON.
    """
    base_url = "https://rest.uniprot.org/uniprotkb/search"
    # Spécifie les champs à retourner : identifiant, nom, gènes, organisme, séquence, longueur, références PDB
    fields = "accession,protein_name,genes,organism_name,sequence,length,xref_pdb"
    params = {
        "query": query,
        "format": "json",
        "fields": fields
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        # En cas d'erreur, on retourne une liste vide
        return []

def get_chembl_medication_data(gene_names, medication_name, medication_interaction):
    """
    Requête simplifiée à l'API ChEMBL pour récupérer des activités/médicaments associés à la protéine.
    Pour cet exemple, on :
      1. Recherche le target ChEMBL à partir du nom du gène.
      2. Utilise cet identifiant pour récupérer quelques activités (médicaments) correspondantes.
    
    Remarque : Le filtre 'medication_interaction' n'est pas directement exploitable via cette API et est ici ignoré.
    """
    # 1. Recherche du target dans ChEMBL
    target_url = "https://www.ebi.ac.uk/chembl/api/data/target/search"
    target_params = {"q": gene_names, "format": "json"}
    target_response = requests.get(target_url, params=target_params)
    if target_response.status_code != 200:
        return []
    
    target_data = target_response.json()
    targets = target_data.get("targets", [])
    if not targets:
        return []
    
    # Pour simplifier, on prend le premier target trouvé
    chembl_target_id = targets[0].get("target_chembl_id")
    if not chembl_target_id:
        return []
    
    # 2. Recherche d'activités associées à ce target
    activity_url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
    # On peut essayer de filtrer par nom de médicament si fourni
    activity_params = {
        "target_chembl_id": chembl_target_id,
        "molecule_pref_name": medication_name if medication_name else "",
        "format": "json",
        "limit": 5
    }
    activity_response = requests.get(activity_url, params=activity_params)
    if activity_response.status_code != 200:
        return []
    
    activity_data = activity_response.json()
    medications = []
    for act in activity_data.get("activities", []):
        medications.append({
            "name": act.get("molecule_pref_name", "Unknown"),
            "interaction": "Unknown",  # Ce champ n'est pas fourni par l'API ChEMBL dans cet endpoint
            "affinity": f"{act.get('standard_value', 'NA')} {act.get('standard_units', '')}",
            "phase": "Unknown",       # Non disponible ici
            "indication": "Unknown"   # Non disponible ici
        })
    return medications

def get_drugbank_medication_data(a_voir):
    target_url = "https://api.drugbank.com/v1/eu"
    target_params = {"q": gene_names, "format": "json"}
    target_response = requests.get(target_url, params=target_params)
    if target_response.status_code != 200:
        return []
    
    target_data = target_response.json()
    targets = target_data.get("targets", [])
    if not targets:
        return []
    
    # Pour simplifier, on prend le premier target trouvé
    chembl_target_id = targets[0].get("target_chembl_id")
    if not chembl_target_id:
        return []
    
    # 2. Recherche d'activités associées à ce target
    activity_url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
    # On peut essayer de filtrer par nom de médicament si fourni
    activity_params = {
        "target_chembl_id": chembl_target_id,
        "molecule_pref_name": medication_name if medication_name else "",
        "format": "json",
        "limit": 5
    }
    activity_response = requests.get(activity_url, params=activity_params)
    if activity_response.status_code != 200:
        return []
    
    activity_data = activity_response.json()
    medications = []
    for act in activity_data.get("activities", []):
        medications.append({
            "name": act.get("molecule_pref_name", "Unknown"),
            "interaction": "Unknown",  # Ce champ n'est pas fourni par l'API ChEMBL dans cet endpoint
            "affinity": f"{act.get('standard_value', 'NA')} {act.get('standard_units', '')}",
            "phase": "Unknown",       # Non disponible ici
            "indication": "Unknown"   # Non disponible ici
        })
    return medications

@app.route('/query', methods=['GET'])
def query():
    # Récupération des filtres depuis les paramètres GET
    gene_names = request.args.get('gene_names', None)
    organism = request.args.get('organism', None)
    ptm = request.args.get('ptm', None)
    pdb = request.args.get('pdb', None)
    medication_name = request.args.get('medication_name', None)
    medication_interaction = request.args.get('medication_interaction', None)

    # Construction de la requête pour Uniprot
    uniprot_query = build_uniprot_query({
        "gene_names": gene_names,
        "organism": organism,
        "ptm": ptm,
        "pdb": pdb
    })
    uniprot_results = get_uniprot_data(uniprot_query)
    print(uniprot_results)

    # Si un filtre médicamenteux est utilisé, enrichir chaque entrée avec des données issues de ChEMBL
    if medication_name or medication_interaction:
        for entry in uniprot_results:
            # Essayer de récupérer le nom du gène depuis l'entrée Uniprot
            genes = entry.get("genes", [])
            if genes:
                gene_text = genes[0].get("value", gene_names)
            else:
                gene_text = gene_names
            med_data = get_chembl_medication_data(gene_text, medication_name, medication_interaction)
            entry["medications"] = med_data
    else:
        # Sinon, renseigner un champ vide pour les médicaments
        for entry in uniprot_results:
            entry["medications"] = []

    return jsonify(uniprot_results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
