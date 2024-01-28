import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

class UC:
    def __init__(self, name, credits):
        self.name = name
        self.grade = None
        self.credits = credits

    def __str__(self):
        return f"{self.name} ({self.credits} ECTS)"

    def __repr__(self):
        return str(self)
    
    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name and self.credits == __value.credits

    def __hash__(self) -> int:
        return hash((self.name, self.credits))

    def set_grade(self, grade):
        self.grade = grade


UCS = []

# URL of the webpage to scrape
URL = 'https://sigarra.up.pt/feup/pt/cur_geral.cur_planos_estudos_view?pv_plano_id=31224&pv_ano_lectivo=2023&pv_tipo_cur_sigla=&pv_origem=CUR'

# Fetch the HTML content of the webpage
response = requests.get(URL)
html_content = response.text

# Create a BeautifulSoup object
soup = BeautifulSoup(html_content, 'html.parser')

# Open a file in write mode to save the extracted data
with open('extracted_data.txt', 'w') as f:
    # Find all elements with class "caixa"
    caixas = soup.find_all(class_='caixa')

    # Iterate over each "caixa" element
    for caixa in caixas:
        try:
            year = caixa.find('a').get_text(strip=True)
            f.write(f"Year: {year}\n")
        except AttributeError:
            pass
        # Find the table inside each "caixa" element
        table = caixa.find('table', class_='dadossz')
        if table:
            # Find all rows in the table
            rows = table.find_all('tr')
            # Iterate over each row and extract UC name and credits
            for row in rows:
                # Find all cells in the row
                cells = row.find_all(['th', 'td'])
                # Extract and write the UC name and credits from the cells
                if len(cells) >= 3:
                    uc_name = cells[2].get_text(strip=True)
                    uc_credits = cells[4].get_text(strip=True)
                    try:
                        if len(uc_credits) == 0: uc_credits = 0
                        else: uc_credits = float(uc_credits.replace(',', '.'))
                        if uc_credits == 0: uc_credits = 1.5
                        f.write(f"UC Name: {uc_name}\n")
                        f.write(f"UC Credits: {uc_credits}\n")
                        f.write('\n')  # Empty line to separate entries

                        # Add UC to the set of UCs
                        uc = UC(uc_name, uc_credits)
                        if uc not in UCS:
                            UCS.append(uc)

                    except ValueError:
                        pass

# Print the number of unique UCs found

print("Data has been saved to extracted_data.txt")
print(f"Found {len(UCS)} unique UCs")

print("\n\n")
data_UCS = [[uc.name, uc.credits, uc.grade] for uc in UCS]
print(tabulate(data_UCS, headers=["UC Name", "UC Credits", "UC Grade"]))
print("\n\n")


