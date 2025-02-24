from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def function_CopyPast(url):

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
        with open("webScrapping_svg.txt", "w", encoding="utf-8") as file:
            file.write(page_content)
            
    finally:
        driver.quit()

def manage_drugbank_information(file_name="webScrapping_svg.txt"):
    with open("webScrapping_svg.txt", "r", encoding="utf-8") as file:
        texte = file.read(page_content)
    
    


file = open("webScrapping_svg.txt", "w", encoding="utf-8")
for line in file.readlines:
    url = line[:-1]
    function_CopyPast(url)
