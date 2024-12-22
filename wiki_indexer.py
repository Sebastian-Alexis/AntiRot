import requests
from bs4 import BeautifulSoup
import json
import re

#put url here - i guess you could change this link based on what generation you want to scrape/translate lol
URL = "https://en.wikipedia.org/wiki/Glossary_of_Generation_Z_slang"

def scrape_wikipedia_glossary(url):
    response = requests.get(url)
    response.raise_for_status()  #check if request worked 

    soup = BeautifulSoup(response.text, "html.parser")
    terms_dict = {}

    #find glossary section
    dl_elements = soup.find_all("dl")
    for dl in dl_elements:
        terms = dl.find_all("dt")
        definitions = dl.find_all("dd")

        for term, definition in zip(terms, definitions):
            # Clean the term and definition
            term_text = term.get_text(strip=True)
            term_text = re.sub(r"\s*\([^)]*\)", "", term_text)  # Remove parenthesis and content inside
            definition_text = definition.get_text(strip=True)
            definition_text = re.sub(r"\[\d+\]", "", definition_text)  # Remove citations like [13][183]
            terms_dict[term_text] = definition_text.strip()

    return terms_dict

def save_to_json(data, filename="definitions.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    print("scraping wikipedia glossary...")
    glossary = scrape_wikipedia_glossary(URL)
    print(f"scraped {len(glossary)} terms")

    print(f"saving to definitions.json...")
    save_to_json(glossary)
    print("finished")
