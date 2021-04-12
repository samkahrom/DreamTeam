# To solve your task you might (or might not) need to import additional libraries
from flask import Flask, render_template, redirect, url_for, request, logging
from datetime import datetime
import calendar
import requests
import json
# import pprint

app = Flask(__name__, static_url_path='/static')

# Headers for REST API call. 
# Paste the API-key you have been provided as the value for "x-api-key"
headers = {
        "Content-Type": "application/json",
        "Accept": "application/hal+json",
        "x-api-key": "860393E332148661C34F8579297ACB000E15F770AC4BD945D5FD745867F590061CAE9599A99075210572",
        }


# Example of function for REST API call to get data from Lime
def get_api_data(headers, url):
    # First call to get first data page from the API
    response = requests.get(url=url,
                            headers=headers,
                            data=None,
                            verify=False)

    # Convert the response string into json data and get embedded limeobjects
    json_data = json.loads(response.text)
    limeobjects = json_data.get("_embedded").get("limeobjects")
    

    # Check for more data pages and get thoose too
    nextpage = json_data.get("_links").get("next")
    while nextpage is not None:
        url = nextpage["href"]
        response = requests.get(url=url,
                                headers=headers,
                                data=None,
                                verify=False)

        json_data = json.loads(response.text)
        limeobjects += json_data.get("_embedded").get("limeobjects")
        nextpage = json_data.get("_links").get("next")
       # value = json_data.get("_embedded").get("limeobjects").get("value")
    return limeobjects


# Index page
@app.route('/')
def index():

    return render_template('home.html')


# Example page

def calcAvgDealValue(data):
    dealCount = len(data) #12 eli lasketaan diilien määrä
    values = [] # alustetaan tyhjä lista 
    for deal in data: # käydään alkuperäinen data läpi ja lisätään listaan jokaisen diilin value kentän arvo
        values.append(deal.get("value")) # append metodi lisää listan perään seuraavan arvon

    def calcSum(arr): # Yksinkertainen yhteenlasku funktio. Käy values - listan läpi ja laskee sen arvot yhteen 
        sum = 0
        for i in arr:
            sum += i # sum = sum + arvo 
        return sum
    # [100, 500, 600 ]
    averageDealValue = calcSum(values) / dealCount # lasketaan keskiarvo
    prettifiedAverage = round(averageDealValue, 1) # pyöristetään keskiarvo yhden desimaalin tarkkuuteen
    return prettifiedAverage

def initMonthObj(obj, months): # Funktion tarkoitus on asettaa olio haluttuun alkutilaan
    # Olion tila tässä {}
    # setMonth ottaa parametriksi olion ja kuukauden nimen ja laittaa sen nimen kohdalle arvoksi 0 esim. January: 0
    def setMonth(obj, name):
        obj[name] = 0
    # Käydään kuukausien nimilista läpi ja kutsutaan setMonth funktiota jokaisen nimen kohdalla 
    for monthName in months:
        setMonth(obj, monthName)
    # Lopuksi palautetaan alustettu olio ulos funktiosta

    return obj


def calcMonthlyDeals(data): 
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    monthlyDeals = {}
    # Olion luonti
    # Lähetetään funktiolle parametrinä, eli muokataan oliota, mukaan myös kuukausien nimet
    monthlyDeals = initMonthObj(monthlyDeals, months)
    # Käydään jälleen api data läpi ja jokaisen diilin kohdalla:
    for deal in data:
        # Haetaan diili json oliosta closeddate parametrin arvo
        dateString = deal.get("closeddate")
        # Parametrin arvo on tyyppiä merkkijono, joten muutetaan se kokonaisluvuksi int() funktiolla, tarvitsemme sitä
        # siinä muodossa seuraavalla rivillä. Funktion sisälle annamme dateString '2020-05-01 12:33:00 +2HM' arvon substringin, eli palan merkkijonoa.
        # Tässä tapausessa otetaan 05 mikä on merkkijonossa indeksipaikalla 5-7
        monthInt = int(dateString[5:7])
        # Haetaan calendar kirjastolla dynaamisesti sen indeksipaikkaan asettamalla kokonaisluku arvolla palautunut kuuauden nimi, tässä 
        # tapauksessa May.
        monthStr = calendar.month_name[monthInt] 
        # Asetetaan May:n arvoksi edellisen kierroksen arvo + 1, eli diilejä on tehty 1 enemmän siinä kuussa
        if monthStr in monthlyDeals:
            monthlyDeals[monthStr] += 1
    print(monthlyDeals)
    
    # Luodaan dictionarysta kuukausien mukaan järjestelty tuple eli
    # aluksi: 
    # {
    #   january: 0,
    #   february: 0
    # }
    # nyt: 
    #  [
    #    (January, 0),
    #    (february, 0)
    #  ]
    # Tein tämän koska en osannut renderöidä jinja templatelle dictionarya kuukausien mukaan järjesteltynä
    sortedTupleOfMonthlyDeals = sorted(monthlyDeals.items(), key=lambda t: months.index(t[0]))
    print(sortedTupleOfMonthlyDeals)
    # Palautetaan funktiosta funktion alussa luotu olio täynnä kuukausia sekä tieto siitä montako closettua diiliä silloin on tapahtunut
    return sortedTupleOfMonthlyDeals

@app.route('/example')
def example():
    # Example of API call to get deals
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = "?_limit=50&dealstatus=agreement&max-closeddate=2020-12-31&min-closeddate=2020-01-01"
    url = base_url + params
    response_deals = get_api_data(headers=headers, url=url)
    calcMonthlyDeals(response_deals)
    
    """
    [YOUR CODE HERE]
    In this exmaple, this is where you can do something with the data in
    'response_deals' before you return it below.
    """
    if len(response_deals) > 0:
        # lähetetään keskiarvo sekä tieto kuukausien diileistä render_template metodin avulla example.html sivulle
        return render_template('example.html', 
            avg=calcAvgDealValue(response_deals), 
            mnth=calcMonthlyDeals(response_deals))
    else:
        msg = 'No deals found'
        return render_template('example.html', msg=msg)


# You can add more pages to your app, like this:
@app.route('/myroute')
def myroute():
    mydata = [{'name': 'kiwi'}, {'name': 'mango'}, {'name': 'banana'}]

    return render_template('mytemplate.html', items=mydata)


"""
You also have to create the mytemplate.html page inside the 'templates'
-folder to be rendered. And then add a link to your page in the 
_navbar.html-file, located in templates/includes/
"""

# DEBUGGING
"""
If you want to debug your app, one of the ways you can do that is to use:
import pdb; pdb.set_trace()
Add that line of code anywhere, and it will act as a breakpoint and halt
your application
"""

if __name__ == '__main__':
    app.secret_key = 'somethingsecret'
    app.run(debug=True)
