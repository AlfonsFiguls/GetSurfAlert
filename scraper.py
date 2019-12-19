import requests
from bs4 import BeautifulSoup
import re

minimumWaveSize = 0.6
minimumPeriodTime = 7

class forecastEntry:
    def __init__(self, date, size, swellDirection, wind, windDirection):
        self.date = date
        self.size = size
        self.swellDirection = swellDirection
        self.wind = wind
        self.windDirection = windDirection


def filterSurfDay(day):
    day = str(day).split("\n")
    sizeWaves = float(re.findall(r">([0-9.]*)<", day[5])[0])
    periodWaves = float(re.findall(r">([0-9.]*)<", day[7])[0])
    if sizeWaves >= minimumWaveSize or periodWaves >= minimumPeriodTime:
        return True
    else:
        return False

def formatSurfData(data):
    formatedData = []
    for e in data:
        sData = str(e).split("</td>")
        date = re.findall(r">([0-9\- :]*)", sData[0])[1]
        size = re.findall(r">([0-9\- :.]*)", sData[4])[0]
        swellDirection = re.findall(r"-([A-Z]*)", sData[5])[0]
        wind = float(re.findall(r">([0-9\- :.]*)", sData[2])[0]) * 3.6
        windDirection = re.findall(r"-([A-Z]*)", sData[3])[0]
        formatedData.append(forecastEntry(date, size, swellDirection, wind, windDirection))
    return formatedData
        


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

filteredgoodDays = formatSurfData(goodSurfingDays)


