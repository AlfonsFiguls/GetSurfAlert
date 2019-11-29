import requests
from bs4 import BeautifulSoup
import re

r = requests.get("http://static.puertos.es/pred_simplificada/Predolas/tablas.html")
soup = BeautifulSoup(r.text, 'html.parser')
data = [str(e) for e in soup.findAll('a') if 'Barcelona' in str(e)] #Getting Barcelona's forecast link
p = re.findall(r"p=([0-9]*)&amp", data[0])[0] #Getting point number


data = { 'point': str(p), 'name': 'Barcelona' }

r = requests.post(url = 'https://bancodatos.puertos.es/TablaAccesoSimplificado/util/get_wanadata.php', data = data)


