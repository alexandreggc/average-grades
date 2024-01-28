from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    global UCS
    if request.method == 'POST':
        # Calculate weighted average grade
        total_credits = 0
        weighted_sum = 0
        for uc in UCS:
            grade = request.form.get(uc.name)
            if grade:
                uc.set_grade(int(grade))
                total_credits += uc.credits
                weighted_sum += uc.credits * int(grade)
            else:
                uc.set_grade(None)
        
        if total_credits > 0:
            average_grade = round(weighted_sum / total_credits, 2)
        else:
            average_grade = 0
        
        return render_template('index.html', UCS=UCS, average_grade=average_grade)
    
    elif request.method == 'GET':

        selected_course = request.args.get('url')
        
        URL = ''  # Initialize URL variable

        if selected_course == 'URLELETRO':
            URL = 'https://sigarra.up.pt/feup/pt/cur_geral.cur_planos_estudos_view?pv_plano_id=31024&pv_ano_lectivo=2023&pv_tipo_cur_sigla=L'
        elif selected_course == 'URLCIVIL':
            URL = 'https://sigarra.up.pt/feup/pt/cur_geral.cur_planos_estudos_view?pv_plano_id=31004&pv_ano_lectivo=2023&pv_tipo_cur_sigla=L'
        elif selected_course == 'URLINFORMATICA':
            URL = 'https://sigarra.up.pt/feup/pt/cur_geral.cur_planos_estudos_view?pv_plano_id=31224&pv_ano_lectivo=2023&pv_tipo_cur_sigla=&pv_origem=CUR'

        if URL:  # Check if URL is not empty
            response = requests.get(URL)
            html_content = response.text

            soup = BeautifulSoup(html_content, 'html.parser')
            caixas = soup.find_all(class_='caixa')

            UCS = []

            for caixa in caixas:
                try:
                    year = caixa.find('a').get_text(strip=True)
                except AttributeError:
                    pass
                table = caixa.find('table', class_='dadossz')
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['th', 'td'])
                        if len(cells) >= 3:
                            uc_name = cells[2].get_text(strip=True)
                            uc_credits = cells[4].get_text(strip=True)
                            try:
                                if len(uc_credits) == 0:
                                    uc_credits = 0
                                else:
                                    uc_credits = float(uc_credits.replace(',', '.'))
                                if uc_credits == 0:
                                    uc_credits = 1.5
                                uc = UC(uc_name, uc_credits)
                                if uc not in UCS:
                                    UCS.append(uc)
                            except ValueError:
                                pass
        else:
            # Handle the case where URL is empty
            print("URL is empty")

        return render_template('index.html', UCS=UCS, average_grade=0, course_select=selected_course)


if __name__ == '__main__':
    app.run(debug=True)
