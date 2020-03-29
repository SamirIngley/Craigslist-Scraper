import os
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import googlemaps
import timeit

api_key = os.environ['GOOGLE_API_KEY']

# modeled on "Python Nerds"'s https://www.youtube.com/watch?v=cFNh2amlYHI&list=PLG3zXM1RkYfTZlZOBc2L6e6aU7IBnzfGN&index=1

# all us based craigslist sites
def cityDict():
    ''' RETURNS A DICTIONARY OF ALL THE CITIES AND THEIR URLS '''

     # HERE'S OUR SOUP - The website html data
    url = 'http://geo.craigslist.org/iso/us/'
    headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1'}
    response = requests.get(url, headers=headers)
    # print(response.status_code)
    # print(response.content)
    soup = bs(response.content, 'html.parser')
    # print(soup.prettify)


    # RETRIEVE ITEMS FROM THE SOUP VIA HTML TAG
    ul_lists = soup.find_all('ul')
    # print(ul_lists[1])

    # THESE DO THE SAME THING
    # city_list = ul_lists[1]
    city_list = soup.find('ul', {'class': 'height6'})


    city_dict = {}

    for city in city_list.find_all('a'): # all urls are in a tags
        city_dict[city.text] = city['href'] # text is name, href is url 
    # print(city_dict)
    return city_dict


def pricesDFrame(c_dict):
    ''' SCRAPES CRAIGSLIST - CREATES A DATAFRAME OF EACH CITY'S TOP 20 ITEMS' 
    PRICE AND CITY '''

    # 'SF bay area': 'https://sfbay.craigslist.org'
    # sf_url = c_dict["SF bay area"]
    # print(sf_url)

    # full_url = sf_url + '/search/sss'
    search_params = { 
                      'sort': 'rel', # SORT BY RELEVANCE.. helps push stuff we don't want to the back of the list
                      'min_price': '50',
                      'mobile_os': '2', # iOS code
                      'query': 'iphone X -cracked -replacement -broken -case -charger', # - means make sure this term is not included
                      'srchType': 'T' #titles only, no garage sale stuff
                    }

    headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1'}


    # r = requests.get(full_url, params=search_params, headers=headers)
    
    # soupty = bs(r.content, 'html.parser')
    # print(soupty.prettify)
    
    price_list = []
    # NAME OF THE CLASSES BY LOOKING ON CRAIGSLIST INSPECT ELEMENT
    # for i,a in enumerate(soupty.find_all('a', {'class': 'result-image gallery'})):
    #     # print('i: ', i)
    #     # print('a: ', a)
    #     price = a.find('span', {'class': 'result-price'}).get_text()
    #     if price and len(price_list) < 20 :
    #         price = int(price[1:])
    #         # print('price ', price)
    #         price_list.append(price) # remove dolla sign

            
    # print(price_list)

    # WE SET THIS UP IN ADVANCE TO ALLOCATE THE MEMORY SO IT GOES FASTER LATER
    # city and price is all the data we care about rn, index gives it the size, arange is just the first value to the last value, num cities*20 is how many we are collecting
    
    df = pd.DataFrame(columns=('city', 'price'), index=np.arange(0,20*len(c_dict)))
    
    index = 0
    for city in c_dict:
        # create a url, make a request, make soup
        # addy = str(city[0])
        # print(addy)
        url = c_dict[city] + '/search/sss'
        # print(url, search_params, headers)
        r = requests.get(url, headers=headers, params=search_params)
        s = bs(r.content, 'html.parser')
        # print(c_dict[city])
        # pull prices from that city (20 max)
        for i,a in enumerate(s.find_all('a', {'class': 'result-image gallery'})):
            # print(i,a)
            price = a.find('span', {'class': 'result-price'}).get_text()
        
            if price and i < 21:
                price = int(price[1:])
                # print(price)
                # push data to df (pandas dataframe)
                df.loc[index] = [city, price]
                index += 1

    print(df.head)

    
    # SAVE TIME BY SAVING AS A FILE INSTEAD OF PINGING CRAIGSLIST EVERYTIME
    # THESE COMMANDS ACTUALLY CREATE THOSE FILES, TIMEIT JUST TIMES THEM
    # pandas can send as csv, to excel, sql, ... 
    #magic commands work in python notebooks- timeit times one loop how long to process one loop
    # %timeit df.to_csv('craigslist_data.csv') #just name it
    # %timeit df.to_excel('craigslist_data.xlsx')
    # %timeit df.to_html('craigslist_data.html') # can open it in a web browser
    # %timeit df.to_hdf('craigslist_data.h5', 'craigslist_data') # for millions of lines, must include a data table name, since we're using strings it's gonna be slower - would be faster with chars and ints

def file_write_locations():
    ''' GETS THE CSV DATA OF THE TWO LISTS (city, price), GETS CITY LOCATION LAT LONG
    AND PUTS INTO A NEW CSV ''' 

    df = pd.read_csv('craigslist_data_copy.csv', index_col=0)
    # print(df)
    city_list = df.city.unique()
    # print(city_list)

    for place in city_list:
        # print(place)
        if type(place) == float:
            continue
        # print(single_place)
        #Geocoding couldn't recognize what the florida keys were soo... 
        # try except: try this, if you run into an error, try this other thing
        # print(df.head)

        try:
            single_place = place.split('/')[0]
            gmaps = googlemaps.Client(key=api_key)
            geocode = gmaps.geocode(single_place)[0]
            latlong = geocode['geometry']['location']
            # print(latlong)
        except IndexError or AttributeError:
            latlong = {'lat': None, 'lng': None}
        
        # now we store the latlong with the associated cities
        # create column called lat
        df.loc[df.city == place, 'lat'] = latlong['lat']
        df.loc[df.city == place, 'lng'] = latlong['lng']
    
    print(df.head)
    print(df.groupby('city').head(1))
    df.to_csv('cities_and_latlongs.csv')

def new():
    df = pd.read_csv('cities_and_latlong.csv', index_col=0)
    df.dropna(inplace=True) # drops NaNs
    print(df.price.mean())
    





    

if __name__ == "__main__":
    # cityDict()
    # pricesDFrame(cityDict())
    # file_write_locations()
    new()