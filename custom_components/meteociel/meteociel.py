import re
import requests
from bs4 import BeautifulSoup
from datetime import date

class WeatherData(object):
    
    def __init__(self, cityCode, day=None, month=None, year=None):
        
        if day == None or month == None or year == None:
            today = date.today()
            self.day = today.day
            self.month = today.month
            self.year = today.year
        else:
            self.day = day
            self.month = month
            self.year = year
        
        # month from 0
        # day from 1
        url = "http://www.meteociel.fr/temps-reel/obs_villes.php?code2=%d&jour2=%d&mois2=%d&annee2=%d&envoyer=OK" % (cityCode, self.day, self.month - 1, self.year)

        table = self.getWeatherTable(url)
        if not table:
            return -1, -1, -1, -1, -1
        self.tmax, self.tmin, self.wind, self.rain, self.sun = self.parseWeatherTable(table)

    def getWeatherTable(self, url):
        
        data = requests.get(url).text
        
        doc = BeautifulSoup(data, features="lxml")
        for table in doc.find_all('table', attrs={'bgcolor': '#FFFF99'}):
            return table
  
    def parseWeatherTable(self, table):
        
        data = table.find_all('tr')[1].find_all('td')
        
        try:
            tmax = float(data[0].text.split(' ')[0])
        except:
            tmax = None
        try:
            tmin = float(data[1].text.split(' ')[0])
        except:
            tmin = None
        try:
            wind = float(data[2].text.split(' ')[0])
        except:
            wind = None
        try:
            rain = float(data[3].text.split(' ')[0])
        except:
            rain = None
        sun = data[4].text
        
        return tmax, tmin, wind, rain, sun
        
             
if __name__ == '__main__':
    data = WeatherData(7235)
    print(data.tmax)
