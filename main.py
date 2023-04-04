from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import datetime


app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    try:
        username = request.json['username']
        password = request.json['password']
    except KeyError:
        return jsonify({'error': 'username or password missing'}), 400
    r = requests.Session()
    login_data = {
        'username': username,
        'password': password
    }
    try:
        r.post(
            'https://itsar.registrodiclasse.it/geopcfp2/update/login.asp?1=1&ajax_target=DIVHidden&ajax_tipotarget=login',
            data=login_data)
        requ = r.get(
            'https://itsar.registrodiclasse.it/geopcfp2/ajax/page/componenti/voti_tabella.asp?idAlunno=2538&idMateria=&idCorsoAnno=210&id=&idUtenteCreazione=&ajax_target=DIV210_&ajax_tipotarget=undefined&z=1680172204309',
            cookies=r.cookies)
    except:
        return jsonify({'error': 'could not access'}), 500
    soup = BeautifulSoup(requ.text, 'html.parser')
    grades = []
    subjects = []
    for row in soup.find_all('tr')[1:]:
        subject = row.td.span.text.strip()
        subjects.append(subject)
        grade = row.findChildren()[2].findChildren()[2].b.text.strip()
        if (grade == "30 lode"):
            grade = 31
        grade = int(grade)
        grades.append(grade)
    materia_voto = res = dict(zip(subjects, grades))
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=30*8) # subtract 8 months
    end_date = today + datetime.timedelta(days=30*8) # add 8 months
    start_date_def = start_date.strftime('%Y-%m-%d')
    end_date_def = end_date.strftime('%Y-%m-%d')
    cal = r.get(f'https://itsar.registrodiclasse.it/geopcfp2/json/fullcalendar_events_alunno.asp?Oggetto=idAlunno&idOggetto=2538&editable=false&z=1680542264288&start={start_date_def}&end={end_date_def}&_=1680542231937').text.strip()
    calendario = json.loads(cal)
    for event in calendario:
        del event['id']
        del event['borderColor']
        del event['backgroundColor']
        del event['rendering']
        del event['overlap']
        del event['editable']
        del event['ClasseEvento']
        del event['tooltip']
        del event['icon']
    final_result = {
        'voti': materia_voto,
        'calendario': calendario
    }
    return jsonify(final_result)

if __name__ == '__main__':
  app.run(port=5000)
