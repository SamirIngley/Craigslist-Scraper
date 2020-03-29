Craigslist Bot
***************
Install:
(best if copy and pasted into a jupyter notebook)

1. clone fork or download this 
2. download the requirements.txt
3. save a google api key as an environment variable
    and use that key variable name in the code
****************
Scrapes the data of every craigslist site in the US
Looks for an item with given parameters

Creates a pandas DataFrame with the price of the item and its city
Retrieves lat and long for each city via Google Maps API

Plots the mean price for each city (eliminating extremes) on a map of the US
The larger the circle - the higher the price. 


Map plotted with Bokeh
