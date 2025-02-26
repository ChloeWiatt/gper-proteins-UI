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
            texte = driver.find_element("tag name", "body").text
            texte_recadre = texte + ",\n"
            fichier.write(texte_recadre)
    
    finally:
        # Fermer le navigateur
        driver.quit()

def manage_drugbank_information(svg_file_name="webScrapping_svg.txt"):
    with open(svg_file_name, "r", encoding="utf-8") as file:
        texte = file.readlines()

    for line in texte[24:374]:
        print(line[:-1])


# Utilisation :
svg_file_name = "webScrapping_svg.txt"
file = open(svg_file_name, "r", encoding="utf-8")
url = "https://www.drugbank.ca/drugs/DB08558"
function_CopyPast(url, svg_file_name)
manage_drugbank_information(svg_file_name)
file.close()
