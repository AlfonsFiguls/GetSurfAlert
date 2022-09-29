import requests
from bs4 import BeautifulSoup
import re
import json
import sys

minimumWaveSize = 0.6
minimumPeriodTime = 6

def returnMsgToSend(date, size, period, swellDirection, wind, windDirection):
    return f"Date: {date}, size: {size}m, period: {period}s, swellDirection: {swellDirection}, wind: {round(wind, 2)}Km/h, windDirection: {windDirection}"

def filterSurfDay(day):
    day = str(day).split("\n")
    sizeWaves = float(re.findall(r"[\d.]+", day[5])[0])
    periodWaves = float(re.findall(r"[\d.]+", day[7])[0])
    if sizeWaves >= minimumWaveSize and periodWaves >= minimumPeriodTime:
        return True
    else:
        return False

def formatSurfData(data):
    sData = str(data).split("</td>")
    date = re.findall(r">([\d\- :]+)", sData[0])[0]
    size = re.findall(r"[\d.]+", sData[4])[0]
    periodWaves = float(re.findall(r"[\d.]+", sData[6])[0])
    swellDirection = re.findall(r">([\w-]+)", sData[5])[0]
    wind = float(re.findall(r">([\d\- :]+)", sData[2])[0]) * 3.6
    windDirection = re.findall(r"-([\w]+)", sData[3])[0]
    return returnMsgToSend(date, size, periodWaves, swellDirection, wind, windDirection)

def sendTelegramMsg(data, telegram):
    sendText = f"https://api.telegram.org/bot{telegram['token']}/sendMessage?chat_id={telegram['chat_id']}&parse_mode=Markdown&text={data}"
    requests.get(sendText)

if __name__ == "__main__":
    telegram = open(sys.argv[1]) #Loading telegram configuration json
    telegram = json.load(telegram)

    r = requests.get("http://static.puertos.es/pred_simplificada/Predolas/tablas.html")
    soup = BeautifulSoup(r.text, 'html.parser')
    data = [str(e) for e in soup.findAll('a') if 'Barcelona' in str(e)] #Getting Barcelona's forecast link
    p = re.findall(r"[\d]+", data[0])[0] #Getting point number

    data = { 'point': str(p), 'name': 'Barcelona' }

    r = requests.post(url = 'https://bancodatos.puertos.es/TablaAccesoSimplificado/util/get_wanadata.php', data = data) #Getting raw forecast data
    soup = BeautifulSoup(r.text, 'html.parser')
    samples = [e for e in soup.findAll('tr') if 'class="datacell"' in str(e)] #Getting forecast data filtered by hours

    goodSurfingDays = filter(filterSurfDay, samples)
    filteredgoodDays = map(formatSurfData, goodSurfingDays)

    for e in filteredgoodDays:
        sendTelegramMsg(e, telegram)
