# Craigslist Bot
This app scrapes the craigslist website for each city/zone across the US and plots a circle of a size with relation to the price of the item for that area. The larger the circle: the higher the price. Data below is for the iPhone X as of March 2020.
***************
## Install:
(best if copy and pasted into a jupyter notebook)

1. Clone, fork, or download this repository
2. pip install requirements.txt
3. If you do not have a Google API key, don't worry, I have already compiled that data in step 5. 
4. Save a google api key as an environment variable and use that key variable name in the code. Can be done temporarily from the terminal this way: export GOOGLE_API_KEY=yourapikeyhere // Check to make sure it was saved with: echo $GOOGLE_API_KEY // This should return your key
5.  This code has a few different functions, one of which returns the latitudes and longitudes of every city using Google's API service. However I already have created that file "cities_and_latlongs.csv" so we do not need to run this function again.

##### 6. Configuring Specifications(product to search for): in pricesDFrame() there's a dictionary search_params which contains the data we search craigslist for in the exact speficications, toggle these to configure your search results. Change the 'query' to the product and anything with a '-' sign in front of it will be removed from the search candidates.  
##### 7. Running the Program: pass cityDict() into pricesDFrame() // pricesDFrame(cityDict()) // upon running this piece of code which calls the two functions we should now have a file called 'craigslist_data_copy.csv'. The function 

****************
- Scrapes the data of every craigslist site in the US for an item with given parameters

- Creates a pandas DataFrame with the price of the item and its city
- Retrieves lat and long for each city via Google Maps API

- Plots the mean price for each city (eliminating extremes) on a map of the US
- The larger the circle - the higher the price. 


Maps plotted with Bokeh


![Alt text](images/us_map.png?raw=true "US Map")

![Alt text](images/NY_map.png?raw=true "NY Map")

![Alt text](images/Texas_map.png?raw=true "Texas Map")



