# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
import time
import csv
import random
from tqdm import tqdm
import re


def clean_text(text):
    """Clean text to remove marketing content and fix formatting"""
    # Remove marketing content
    text = re.sub(
        r"Reduce drug development failure rates.*?SEE HOW", "", text, flags=re.DOTALL
    )
    text = re.sub(r"Improve decision support.*?SEE THE DATA", "", text, flags=re.DOTALL)
    text = re.sub(r"LEARN MORE", "", text)

    # Replace multiple line breaks with a single space
    text = re.sub(r"\n+", " ", text)

    # Remove excess whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def scrape_drugbank_selenium(
    drugbank_ids=[
        "DB08558",
        "DB08347",
        "DB01193",
        "DB00866",
        "DB01118",
        "DB00182",
        "DB01102",
        "DB01238",
        "DB09204",
        "DB06216",
        "DB00335",
        "DB09013",
        "DB00195",
        "DB00217",
        "DB01295",
        "DB00612",
        "DB08807",
        "DB06726",
        "DB08808",
        "DB00248",
        "DB00521",
        "DB01136",
        "DB04846",
        "DB01407",
        "DB00785",
        "DB01151",
        "DB11273",
        "DB13345",
        "DB11278",
        "DB00841",
        "DB04855",
        "DB06262",
        "DB01363",
        "DB01364",
        "DB00668",
        "DB01049",
        "DB00187",
        "DB01288",
        "DB00983",
        "DB00221",
        "DB01064",
        "DB00598",
        "DB00555",
        "DB09351",
        "DB01210",
        "DB00408",
        "DB01365",
        "DB01214",
        "DB00264",
        "DB08893",
        "DB01203",
        "DB04861",
        "DB00368",
        "DB00540",
        "DB00334",
        "DB01580",
        "DB00715",
        "DB01359",
        "DB00397",
        "DB00960",
        "DB01291",
        "DB01297",
        "DB01182",
        "DB00571",
        "DB00852",
        "DB01917",
        "DB11124",
        "DB00243",
        "DB00867",
        "DB01001",
        "DB00938",
        "DB00489",
        "DB03566",
        "DB00127",
        "DB00871",
        "DB00373",
        "DB00726",
        "DB09068",
        "DB13781",
        "DB00181",
        "DB00452",
        "DB12698",
        "DB05501",
        "DB14939",
        "DB12715",
        "DB06809",
        "DB12018",
    ]
):
    # Setup driver options
    options = EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--inprivate")
    options.use_chromium = True

    # Add more browser options
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-web-security")
    options.add_argument("--enable-features=NetworkServiceInProcess")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.64"
    )

    print("Initializing Edge driver...")
    driver = webdriver.Edge(
        service=EdgeService(EdgeChromiumDriverManager().install()), options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    # DrugBank IDs
    print(f"Starting to scrape {len(drugbank_ids)} DrugBank entries...")

    # Define output file and headers
    output_file = "drugbank_data.csv"
    headers = [
        "DrugBank ID",
        "Name",
        "Accession Number",
        "Type",
        "Groups",
        "Description",
        "Synonyms",
        "Brand Names",
        "Indication",
        "Pharmacodynamics",
        "Mechanism of Action",
        "Absorption",
        "Metabolism",
        "Route of Elimination",
        "Half Life",
        "Protein Binding",
        "Adverse Effects",
        "Contraindications",
        "Drug Interactions",
        "Food Interactions",
        "Affected Organisms",
        "Chemical Formula",
        "Molecular Weight",
        "IUPAC Name",
        "CAS Number",
        "SMILES",
        "InChI",
        "InChIKey",
        "UNII",
        "ATC Codes",
        "Categories",
        "Patents",
        "Spectra",
        "References",
    ]

    # Create a list to store all drug data before writing to CSV
    all_drug_data = []

    for drugbank_id in tqdm(drugbank_ids):
        # Initialize drug data with ID
        drug_data = {"DrugBank ID": drugbank_id}

        try:
            # Visit the page
            url = f"https://go.drugbank.com/drugs/{drugbank_id}"
            print(f"Accessing URL: {url}")
            driver.get(url)

            # Optional: Save screenshot and source for debugging
            driver.save_screenshot(f"{drugbank_id}_page.png")
            with open(f"{drugbank_id}_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            # Wait for page to load
            time.sleep(random.uniform(3, 7))

            # Check for access denied
            if (
                "Page not found" in driver.title
                or "Access denied" in driver.page_source
            ):
                print(f"Failed to access {drugbank_id} - access denied or not found")
                continue

            # Extract name
            try:
                name_elem = driver.find_element(By.TAG_NAME, "h1")
                drug_data["Name"] = clean_text(name_elem.text.strip())
                print(f"Found drug name: {drug_data['Name']}")
            except Exception as e:
                print(f"Could not extract Name: {str(e)}")

            # Define field mappings
            field_mappings = {
                "Accession Number": "Accession Number",
                "Type": "Type",
                "Groups": "Groups",
                "Description": "Description",
                "Synonyms": "Synonyms",
                "Brand Names": "Brand Names",
                "Indication": "Indication",
                "Pharmacodynamics": "Pharmacodynamics",
                "Mechanism of Action": "Mechanism of action",
                "Absorption": "Absorption",
                "Metabolism": "Metabolism",
                "Route of Elimination": "Route of elimination",
                "Half Life": "Half life",
                "Protein Binding": "Protein binding",
                "Adverse Effects": "Adverse Effects",
                "Contraindications": "Contraindications",
                "Drug Interactions": "Drug Interactions",
                "Food Interactions": "Food Interactions",
                "Affected Organisms": "Affected organisms",
                "Chemical Formula": "Chemical Formula",
                "Molecular Weight": "Molecular Weight",
                "IUPAC Name": "IUPAC Name",
                "CAS Number": "CAS number",
                "SMILES": "SMILES",
                "InChI": "InChI",
                "InChIKey": "InChI Key",
                "UNII": "UNII",
                "ATC Codes": "ATC Codes",
                "Categories": "Categories",
                "Patents": "Patents",
                "Spectra": "Spectra",
                "References": "References",
            }

            # Extract each field
            for csv_field, html_label in field_mappings.items():
                try:
                    # More precise XPath to find exactly the field we want
                    xpath = f"//dt[normalize-space(text())='{html_label}']/following-sibling::dd[1]"
                    element = driver.find_element(By.XPATH, xpath)
                    value = clean_text(element.text.strip())
                    drug_data[csv_field] = value
                    print(f"Found {csv_field}: {value[:50]}...")  # Print first 50 chars
                except Exception as e:
                    print(f"Could not extract {csv_field}: {str(e)}")
                    drug_data[csv_field] = (
                        ""  # Set empty value rather than leaving field out
                    )

            # Add this drug's data to our collection
            all_drug_data.append(drug_data)
            print(f"Successfully scraped {drugbank_id}")

        except Exception as e:
            print(f"Error processing {drugbank_id}: {str(e)}")

        # Delay between requests
        time.sleep(random.uniform(5, 10))

    # Write all data to CSV at once
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_drug_data)

    driver.quit()
    print(f"Scraping completed! Data saved to {output_file}")


# Call the function to execute
if __name__ == "__main__":
    print("Starting DrugBank scraper...")
    scrape_drugbank_selenium()
