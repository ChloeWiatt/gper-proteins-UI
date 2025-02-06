import requests

def get_drugbank_gper_data():
    target_url = "https://api.drugbank.com/v1/targets"
    target_params = {"q": "GPER", "format": "json"}
    
    target_response = requests.get(target_url, params=target_params)
    if target_response.status_code != 200:
        return []
    
    target_data = target_response.json()
    targets = target_data.get("targets", [])
    if not targets:
        return []
    
    print("Target API Response:", target_response.text)
    
    drugbank_target_id = targets[0].get("drugbank_id")
    if not drugbank_target_id:
        return []
    
    # Recherche des médicaments liés à ce target
    drug_url = f"https://api.drugbank.com/v1/targets/{drugbank_target_id}/drugs"
    drug_response = requests.get(drug_url)
    if drug_response.status_code != 200:
        return []
    
    drug_data = drug_response.json()
    print("Drug API Response:", drug_response.text)
    medications = []
    for drug in drug_data:
        medications.append({
            "name": drug.get("name", "Unknown"),
            "interaction": drug.get("interaction", "Unknown"),
            "affinity": drug.get("affinity", "Unknown"),
            "phase": drug.get("phase", "Unknown"),
            "indication": drug.get("indication", "Unknown")
        })
    
    return medications

# Exemple d'utilisation
medications = get_drugbank_gper_data()
for med in medications:
    print(med)
