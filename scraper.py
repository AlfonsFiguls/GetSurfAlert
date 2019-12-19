import requests
from bs4 import BeautifulSoup
import re
import json
import sys

minimumWaveSize = 0.6
minimumPeriodTime = 7

class forecastEntry:
    def __init__(self, date, size, swellDirection, wind, windDirection):
        self.date = date
        self.size = size
        self.swellDirection = swellDirection
        self.wind = wind
        self.windDirection = windDirection
    def printForecast(self):
        print('Date: {0}, size: {1}, swellDirection: {2}, wind: {3}, windDirection: {4}'.format(self.date, self.size, self.swellDirection, round(self.wind, 2), self.windDirection))
    def getForecast(self):
        return 'Date: {0}, size: {1}, swellDirection: {2}, wind: {3}, windDirection: {4}\n'.format(self.date, self.size, self.swellDirection, round(self.wind, 2), self.windDirection)


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
        formatedData.append(forecastEntry(date, size, swellDirection, wind, windDirection)) #Appending forecast object data instead of a string for future work on the independent values.
    return formatedData

def sendTelegramMsg(data, telegram):
    sendText = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&parse_mode=Markdown&text={2}'.format(telegram['token'], telegram['chat_id'], data)
    requests.get(sendText)
        
telegram = open(sys.argv[1]) #Loading telegram configuration json
telegram = json.load(telegram)

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

for e in filteredgoodDays:
    sendTelegramMsg(e.getForecast(), telegram)
