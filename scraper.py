import requests
from bs4 import BeautifulSoup
import re

minimumWaveSize = 0.6
minimumPeriodTime = 7

def filterSurfDay(day):
    day = str(day).split("\n")
    sizeWaves = float(re.findall(r">([0-9.]*)<", day[5])[0])
    periodWaves = float(re.findall(r">([0-9.]*)<", day[7])[0])
    if sizeWaves >= minimumWaveSize or periodWaves >= minimumPeriodTime:
        return True
    else:
        return False


r = requests.get("http://static.puertos.es/pred_simplificada/Predolas/tablas.html")
soup = BeautifulSoup(r.text, 'html.parser')
data = [str(e) for e in soup.findAll('a') if 'Barcelona' in str(e)] #Getting Barcelona's forecast link
p = re.findall(r"p=([0-9]*)&amp", data[0])[0] #Getting point number


data = { 'point': str(p), 'name': 'Barcelona' }

r = requests.post(url = 'https://bancodatos.puertos.es/TablaAccesoSimplificado/util/get_wanadata.php', data = data) #Getting raw forecast data
soup = BeautifulSoup(r.text, 'html.parser')
samples = [e for e in soup.findAll('tr') if 'class="datacell"' in str(e)] #Getting forecast data filtered by hours

goodSurfingDays = []
for e in samples:
    if filterSurfDay(e):
        goodSurfingDays.append(e)

print(goodSurfingDays)

