import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs

# modeled on Python Nerds https://www.youtube.com/watch?v=cFNh2amlYHI&list=PLG3zXM1RkYfTZlZOBc2L6e6aU7IBnzfGN&index=1

# all us based craigslist sites
def cityDict():
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


def bot(c_dict):

    # 'SF bay area': 'https://sfbay.craigslist.org'
    sf_url = c_dict["SF bay area"]
    # print(sf_url)

    full_url = sf_url + '/search/sss'
    search_params = { 
                      'sort': 'rel', # SORT BY RELEVANCE.. helps push stuff we don't want to the back of the list
                      'min_price': '50',
                      'mobile_os': '2', # iOS code
                      'query': 'iphone X -cracked -replacement -broken -case -charger', # - means make sure this term is not included
                      'srchType': 'T' #titles only, no garage sale stuff
                    }

    headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1'}


    r = requests.get(full_url, params=search_params, headers=headers)
    
    soupty = bs(r.content, 'html.parser')
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

if __name__ == "__main__":
    cityDict()
    bot(cityDict())