from fastapi import FastAPI
import logging
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from models import Rankings, Advisor, Papers, University, DataModel

app = FastAPI()

CSV_URL = "https://csrankings.org/csrankings.csv"

# https://csrankings.org/#/index?vision
cs_categories = {
    "ai": "Artificial intelligence",
    "vision": "Computer vision",
    "mlmining": "Machine Learning",
    "nlp": "Natural language processing",
    "inforet": "The Web & information retrieval",
    "arch": "Computer architecture",
    "comm": "Computer networks",
    "sec": "Computer security",
    "mod": "Databases",
    "da": "Design automation",
    "bed": "Embedded & real-time systems",
    "hpc": "High-performance computing",
    "mobile": "Mobile computing",
    "metrics": "Measurement & perf. analysis",
    "ops": "Operating systems",
    "plan": "Programming languages",
    "soft": "Software engineering",
    "act": "Algorithms & complexity",
    "crypt": "Cryptography",
    "log": "Logic & verification",
    "graph": "Computer graphics",
    "bio": "Comp. bio & bioinformatics",
    "csed": "Computer science education",
    "ecom": "Economics & computation",
    "chi": "Human-computer interaction",
    "robotics": "Robotics",
    "visualization": "Visualization",
}


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/scrap", response_model=DataModel)
def scrap():
    # Configurar opciones de Chrome para modo headless
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    scraped_data = DataModel(universities=[])

    for k, category in cs_categories.items():
        browser = webdriver.Chrome(options=options)
        base_url = "https://csrankings.org/#/index?{}&us"
        url = base_url.format(k)
        logging.info(f"Scraping data for {category} from {url}")
        print(f"Scraping data for {category} from {url}")
        browser.get(url)
        time.sleep(2)  # Esperar a que cargue la página

        soup = BeautifulSoup(browser.page_source, "html.parser")

        table = soup.select_one("#ranking")
        if not table:
            logging.warning(f"Failed to retrieve data for {category}")
            browser.quit()
            continue

        tbody = table.find("tbody")
        if not tbody:
            logging.warning(f"Failed to retrieve tbody for {category}")
            browser.quit()
            continue

        rows = tbody.find_all("tr", recursive=False)

        for i in range(0, len(rows), 3):
            # Extraer ranking y nombre de la universidad
            rank_text = rows[i].find("td").text.strip()
            try:
                rank = int(rank_text)
            except ValueError:
                rank = 0  # O manejar de otra manera si el ranking no es un número

            u_name = rows[i].find_all("td")[1].find_all("span")[1].text.strip()
            logging.info(f"Category: {category} | Rank: {rank} | University: {u_name}")

            # Verificar si la universidad ya está en scraped_data
            university = next((u for u in scraped_data.universities if u.name == u_name), None)
            if not university:
                university = University(name=u_name, rankings=Rankings(), advisors=[])
                scraped_data.universities.append(university)

            # Actualizar el ranking para la categoría actual
            setattr(university.rankings, k, rank)

            # Procesar asesores
            try:
                faculties_row = rows[i + 2]
            except IndexError:
                logging.warning(f"No faculty row found for {u_name} in category {category}")
                continue

            faculties_table = faculties_row.find("table")
            if not faculties_table:
                logging.warning(f"Failed to retrieve faculties for {u_name} in category {category}")
                continue
            faculties_tbody = faculties_table.find("tbody")
            if not faculties_tbody:
                logging.warning(f"Failed to retrieve faculties tbody for {u_name} in category {category}")
                continue

            faculties_rows = faculties_tbody.find_all("tr")
            for j in range(0, len(faculties_rows), 2):
                faculty_link = faculties_rows[j].find("a")
                if not faculty_link:
                    logging.warning(f"Missing link for faculty in {u_name} for category {category}")
                    continue
                faculty_name = faculty_link.text.strip()
                faculty_href = faculty_link.get("href")

                faculty_no_pub_text = faculties_rows[j].find_all("td")[2].find("a").text.strip()
                try:
                    faculty_no_pub = int(faculty_no_pub_text)
                except ValueError:
                    faculty_no_pub = 0  # O manejar de otra manera

                logging.info(f"Faculty: {faculty_name} | Href: {faculty_href} | Papers in {category}: {faculty_no_pub}")

                # Buscar si el asesor ya existe en la universidad
                advisor = next((a for a in university.advisors if a.href == faculty_href), None)
                if not advisor:
                    advisor = Advisor(name=faculty_name, href=faculty_href, papers=Papers())
                    university.advisors.append(advisor)

                # Actualizar el número de publicaciones en la categoría actual
                setattr(advisor.papers, k, faculty_no_pub)

        browser.quit()
    
    print(scraped_data)
    return scraped_data
