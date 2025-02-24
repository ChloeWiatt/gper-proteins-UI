from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def function_CopyPast(url, svg_file_name="webScrapping_svg.txt"):

    # Configuration de Firefox
    options = Options()
    options.headless = True  # Exécution sans interface graphique (optionnel)
    # Initialisation du driver
    driver = webdriver.Firefox(options=options)
    
    try:
        driver.get(URL)
        # Attente implicite pour le chargement de la page
        driver.implicitly_wait(10)
        # Récupération du contenu de la page
        page_content = driver.page_source
        # Écriture dans le fichier
        with open(svg_file_name, "w", encoding="utf-8") as file:
            file.write(page_content)
            
    finally:
        driver.quit()

def manage_drugbank_information(svg_file_name="webScrapping_svg.txt"):
    with open(svg_file_name, "r", encoding="utf-8") as file:
        texte = file.read(page_content)
    
    texte = texte[25:417]


# Utilisation :
svg_file_name = "webScrapping_svg.txt"
file = open(svg_file_name, "w", encoding="utf-8")
for line in file.readlines:
    url = line[:-1]
    function_CopyPast(url, svg_file_name)
    manage_drugbank_information(svg_file_name)
