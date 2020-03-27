import requests
from bs4 import BeautifulSoup as bs

# modeled on Python Nerds https://www.youtube.com/watch?v=cFNh2amlYHI&list=PLG3zXM1RkYfTZlZOBc2L6e6aU7IBnzfGN&index=1

# all us based craigslist sites
def bot():

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

    # 'SF bay area': 'https://sfbay.craigslist.org'
    sf_url = city_dict["SF bay area"]
    # print(sf_url)

    full_url = sf_url + '/search/sss'
    search_params = { 
                      'sort': 'rel',
                      'min_price': '50',
                      'mobile_os': '2', # iOS code
                      'query': 'iphone X -cracked -replacement -broken -case -charger', # - means make sure this term is not included
                      'srchType': 'T' #titles only, no garage sale stuff
                    }

    r = requests.get(full_url, params=search_params, headers=headers)
    
    soupty = bs(r.content, 'html.parser')
    # print(soupty.prettify)
    
    price_list = []
    for i,a in enumerate(soupty.find_all('a')):
        # print('i: ', i)
        # print('a: ', a)
        price = a.find('span', {'class': 'result-price'})
        if price:
            price = price.get_text()
            # print('price ', price)
            price_list.append(price)
            
    print(price_list)

bot()