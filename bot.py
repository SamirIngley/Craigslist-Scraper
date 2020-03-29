import os
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import googlemaps
from bokeh.io import show, output_file
from bokeh.models import (GMapPlot, GMapOptions, ColumnDataSource, 
Circle, DataRange1d, Range1d, PanTool, WheelZoomTool, BoxSelectTool)
import timeit

api_key = os.environ['GOOGLE_API_KEY']

# modeled on "Python Nerds"'s https://www.youtube.com/watch?v=cFNh2amlYHI&list=PLG3zXM1RkYfTZlZOBc2L6e6aU7IBnzfGN&index=1
# CRAIGSLIST USES A STANDARD / KNOWN URL QUERY FOR ITS WEBSITES
# PARAMETERS IN pricesDFrame() -> SEARCH_PARAMS OR stats()

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
    print(df.groupby('city').head(1)) # 1 from each
    df.to_csv('cities_and_latlongs.csv')



def stats():
    ''' REMOVES EXTREME PRICES '''

    df = pd.read_csv('cities_and_latlongs.csv', index_col=0)
    df = df[df.price < 1000] # reassigned df to itself, subset of iteself with values only under 1000

    df.dropna(inplace=True) # drops NaNs
    print('mean: ', df.price.mean()) # df.mean() gives a mean of all the columns
    print('median: ', df.price.median())

    print('HEAD')
    print(df[['city', 'price']].sort_values(by='price').head(30))

    print('TAIL')
    print(df[['city', 'price']].sort_values(by='price').tail(30)) # DEFAULT IS DESCENDING ORDER, 30 - last thirty, gives us the last thirty prices to see why our mean and median are so off

    df = df[df.price < 1000] # reassigned df to itself, subset of iteself with values only under 1000

    print('STD: ', df.price.std())
    # 3 of your standard deviation should get you most of your values (98%)
    # so to get our upper and lower bounds
    print(df.price.mean() - 3 * df.price.std())
    print(df.price.mean() + 3 * df.price.std())

    # Visualize using %matplotlib inline if using jupyter
    # print(df.price.hist(bins=50))
    df.to_csv('df_clean.csv')



def map_data():
    df0 = pd.read_csv('df_clean.csv', index_col=0) # need to tell pandas the first row is an index column

    df = df0.groupby('city').mean() # gives us the MEAN PRICE FOR EACH CITY
    # print(df.head)

    # Google maps has control over plot axes so no DataRange1d, only Range1d
    map_options = GMapOptions(lat=50.5020794, lng=-111.9912878, map_type='satellite', zoom=3) # LAT LNG ARE ROUGHLY THE CENTER OF THE MAP
    plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options,
                    api_key=api_key)

    plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool())

    # ranges for our circles in bokeh (gliphs)
    baseline = df['price'].min() - 1.0 # smallest price is smallest dot
    scale = 10.4
    # latitude and longitude for the circles (gliphs) on the map, dict in this column format 
    # radius is scaling, i is price, subtracting baseline by a scale so the circles fit
    source = ColumnDataSource(data=dict(lat=df['lat'].tolist(), lon=df['lng'].tolist(), 
                                        rad = [(i-baseline) / scale for i in df['price'].tolist()]))
    
    circle = Circle(x="lon", y="lat", size="rad", fill_color="blue", fill_alpha=0.5) # alpha makes transparent
    plot.add_glyph(source, circle)
    # print(plot.add_glyph(source, circle)

    output_file('USA_plot.html')
    show(plot)




if __name__ == "__main__":
    # cityDict()
    # pricesDFrame(cityDict())
    # file_write_locations()
    # stats()
    map_data()