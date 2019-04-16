# dependencies
import pandas as pd
from bs4 import BeautifulSoup as bs
import os
import time
from splinter import Browser
from urllib.parse import urlsplit
from selenium import webdriver
import requests

def init_browser():
    # chromedriver executable path
    executable_path = {'executable_path': 'c:/chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)
    
def scrape():
    browser = init_browser()
    mars_facts_data = {}

    # visit Mars news url
    mars_url = 'https://mars.nasa.gov/news/'
    browser.visit(mars_url)
    time.sleep(8)

    # write to html with bs
    html = browser.html
    soup = bs(html,'html.parser')

    # collect news_title and <p> text, assign the text to variables
    news_title = soup.find('div', class_='content_title').text
    news_p = soup.find('div', class_='article_teaser_body').text
    mars_facts_data['news_title'] = news_title
    mars_facts_data['news_p'] = news_p

    # visit the url for JPL Featured Space Image
    img_url_featured = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(img_url_featured)
    time.sleep(3)

    # find the featured image fullsize url with bs
    html_image = browser.html
    soup = bs(html_image, "html.parser")

    featured_img_url = soup.find('article')['style'].replace('background-image: url(','').replace(');', '')[1:-1]

    main_url = 'https://www.jpl.nasa.gov'
    featured_image_url = main_url + featured_img_url
    mars_facts_data['featured_image'] = featured_img_url

    # visit url to collect Mars weather
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)
    time.sleep(8)

    # scrape the latest weather with bs
    weather_html = browser.html
    soup = bs(weather_html, 'html.parser')
    mars_weather = soup.find('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text
    mars_facts_data['mars_weather'] = mars_weather

    # set url where we will scrape Mars facts
    facts_url = 'https://space-facts.com/mars/'

    scrape_table = pd.read_html(facts_url)
    scrape_table[0]

    # load scraped table into dataframe, set titles
    mars_facts_df = scrape_table[0]
    mars_facts_df.rename(columns={0: 'Fact', 1: 'Value'}, inplace=True)
    mars_facts_df.set_index('Fact')
    
    # transform to html table
    mars_html_table = mars_facts_df.to_html()
    mars_html_table.replace('\n', '')
    mars_facts_data['mars_facts_table'] = mars_html_table

    # set url where we will scrape hemispheres images
    hemispheres_main_url = "https://astrogeology.usgs.gov"
    hemispheres_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    
    # Retrieve page with the requests module
    response = requests.get(hemispheres_url)
    
    # create bs object and visit url
    soup = bs(response.text, 'html.parser')
    browser.visit(hemispheres_url)

    # parse html with bs
    html = browser.html
    soup = bs(html, 'html.parser')

    # results are returned as an iterable list
    hemispheres = soup.find_all('a', class_="itemLink")

    # Loop through returned results
    hemisphere_img_urls = []

    for result in hemispheres:

        try:
            # find title
            title = result.find('h3').text

            # find link
            link = result['href']
            print("title: ", title)

            # use the full url
            full_link = hemispheres_main_url + link
            print("full-link: ", full_link)

            # go to the link to get to the page with the full image
            response = requests.get(full_link)
            # parse with bs 
            soup = bs(response.text, 'html.parser')

            try:

                # get full image url from href
                download = soup.find('div', class_='downloads')
                full_href = download.find('a')['href']
                print("full_href: ", full_href)

                # put title and image URL into dictionary
                hemisphere_img_urls.append({"title": title, "img_url": full_href})


            except Exception as f:
                print("f: ", f)

        except Exception as e:
            print("e: ", e)

        mars_facts_data['hemisphere_img_url'] = hemisphere_img_urls

    return mars_facts_data