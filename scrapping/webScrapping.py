import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def function_CopyPast(url, svg_file_name="webScrapping_svg.txt"):

    # Initialiser le navigateur Firefox
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Optionnel : pour un mode sans interface graphique
    driver = webdriver.Firefox(options=options)

    try:
        # Ouvrir la page web
        driver.get(url)
        time.sleep(1)  # Attendre que la page se charge

        """
        # Trouver la barre de recherche (ajustez le sélecteur CSS selon la page)
        search_box = driver.find_element("css selector", "input[type='text']")  # Changez le sélecteur si nécessaire
        search_box.send_keys(mot_cle)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Attendre les résultats
        """ 
        
        # Sélectionner tout le contenu de la page
        body = driver.find_element("tag name", "body")
        body.send_keys(Keys.CONTROL, 'a')  # CTRL + A
        body.send_keys(Keys.CONTROL, 'c')  # CTRL + C

        # Récupérer le contenu copié et l'enregistrer dans un fichier texte
        with open(svg_file_name, "w", encoding="utf-8") as fichier:
            text = driver.find_element("tag name", "body").text
            text_reshape = text + ",\n"
            fichier.write(text_reshape)
    
    finally:
        # Fermer le navigateur
        driver.quit()

def manage_drugbank_information(svg_file_name="webScrapping_svg.txt"):
    with open(svg_file_name, "r", encoding="utf-8") as file:
        texte = file.readlines()

    # Get Information from the svg_file_name :
    ligne_index = 0
    ## RECOMMENDED FOR PHARMA :
    while texte[ligne_index][:-1] != "DrugBank ID":
        ligne_index += 1
    ### Clinical Trials (Phases)
    while texte[ligne_index][:-1] != "Clinical Trials":
        ligne_index += 1
    ligne_index += 1
    Phases_list = []
    while texte[ligne_index][:5] == "Phase":
        ligne_index += 1
        Phases_list.append(texte[ligne_index][:-1])
        ligne_index += 1
    ClinicalTrials_Phases = "[" + " ;".join(Phases_list) + "]"
    ## IDENTIFICATION :
    ### Generic Name
    while texte[ligne_index][:-1] != "Generic Name":
        ligne_index += 1
    ligne_index += 1
    Generic_Name = texte[ligne_index][:-1].replace(",", ";")
    ### DrugBank ID
    ligne_index += 2
    DrugBank_ID = texte[ligne_index][:-1]
    ### Background
    ligne_index += 2
    Background = texte[ligne_index][:-1]
    if Background == "Not Available":
        Background = ""
    ### Type
    ligne_index += 2
    Type = texte[ligne_index][:-1]
    ### Groups
    ligne_index += 2
    Groups = texte[ligne_index][:-1]
    ### Weight
    while texte[ligne_index][:-1] != "Weight":
        ligne_index += 1
    ligne_index += 1
    Weight_Average = texte[ligne_index][9:-1]
    ligne_index += 1
    Weight_Monoisotopic = texte[ligne_index][14:-1]
    ### Chemical Formula
    ligne_index += 2
    Chemical_Formula = texte[ligne_index][:-1]
    ## Categories
    ### Description
    while texte[ligne_index][:-1] != "Description":
        ligne_index += 1
    ligne_index += 1
    Description = texte[ligne_index][:-1]
    ### Kingdom
    ligne_index += 2
    Kingdom = texte[ligne_index][:-1]
    ### Super Class
    ligne_index += 2
    Super_Class = texte[ligne_index][:-1]
    ### Class
    ligne_index += 2
    Class = texte[ligne_index][:-1]
    ### Sub Class
    ligne_index += 2
    Sub_Class = texte[ligne_index][:-1]
    ### Direct Parent
    ligne_index += 2
    Direct_Parent = texte[ligne_index][:-1]
    ### Alternative Parents
    ligne_index += 2
    Alternative_Parents = "[" + "; ".join(texte[ligne_index][:-1].split(sep=" / ")) + "]"
    ### Substituents
    ligne_index += 2
    Substituents = "[" + "; ".join(texte[ligne_index][:-1].split(sep=" / ")) + "]"
    ### Molecular Framework
    ligne_index += 2
    Molecular_Framework = texte[ligne_index][:-1]
    ### External Descriptors
    ligne_index += 2
    External_Descriptors = texte[ligne_index][:-1]
    if External_Descriptors == "Not Available":
        External_Descriptors = ""
    
    with open("drugbank.csv", "a", encoding="utf-8") as file:
        file.write(f"{DrugBank_ID}, {Generic_Name}, {Background}, {Type}, {Groups}, {Weight_Average}, \
{Weight_Monoisotopic}, {Chemical_Formula}, {ClinicalTrials_Phases}, {Description}, {Kingdom}, \
{Super_Class}, {Class}, {Sub_Class}, {Direct_Parent}, {Alternative_Parents}, {Substituents}, \
{Molecular_Framework}, {External_Descriptors}\n")


# Utilisation :
url_file = open("drugbank_url.txt", "r", encoding="utf-8")
for line in url_file.readlines():
    url = line[:-1]
    function_CopyPast(url, "webScrapping_svg.txt")
    manage_drugbank_information("webScrapping_svg.txt")
url_file.close()
