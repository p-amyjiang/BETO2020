import selenium
from selenium import webdriver
import numpy as np
import pandas as pd
import bs4
from bs4 import BeautifulSoup
import time

"""
This code is used to scrape Wiley Online of publication urls and write them to
a text file in the current directory for later use.

"""

def scrape_page(driver):
    """
    This method finds all hrefs on webpage
    """

    elems = driver.find_elements_by_xpath("//a[@href]")
    return elems


def clean(elems):
    """
    This method takes a list of scraped selenium web elements
    and filters/ returns only the hrefs leading to publications.
    """

    urls = []
    for elem in elems:
        url = elem.get_attribute("href")
        if 'doi' in url and 'pdf' not in url\
                            and 'search' not in url\
                            and 'abs' not in url\
                            and 'full' not in url\
                            and 'show=' not in url:
            urls.append(url)
    return urls

def build_annual_urls(search_term,year):
    """
    This method takes the first Wiley url and creates a list of
    urls which lead to the following pages on Wiley which will be
    scraped. 
    """
    
    page_urls = []
    for i in range(20):
        url_100 = 'https://onlinelibrary.wiley.com/action/doSearch?AllField=' + search_term.replace(" ", "+") + '&content=articlesChapters&countTerms=true&target=default&pageSize=100'
        urli = url_100 + '&AfterYear=' + str(year) + '&BeforeYear=' + str(year) + '&startPage=' + str(i)
        page_urls.append(urli)

    return page_urls

def scrape_all(search_term,driver, year):
    """
    This method takes the first ACS url and navigates
    through all pages of listed publications, scraping each url
    on each page. Returns a list of the urls.
    """
    page_list = build_annual_urls(search_term,year)
    urls = []
    for page in page_list:
        driver.get(page)
        time.sleep(1) #must sleep to allow page to load
        elems = scrape_page(driver)
        links = clean(elems)
        if urls != [] and links[0] == urls[0]:
            break
        for link in links:
            urls.append(link)


    return urls


def proxify(scraped_urls,prefix):
    """
    This method takes a list of scraped urls and turns them into urls that
    go through the UW Library proxy so that all of them are full access.
    """

    proxy_urls = []
    for url in scraped_urls:
        sd_id = url[32:]
        newlink = prefix + sd_id
        proxy_urls.append(newlink)

    return proxy_urls

def write_urls(urls,filename):
    """
    This method takes a list of urls and writes them to a desired text file.
    """
    file = open(filename,'w')
    for link in urls:
        file.write(link)
        file.write('\n')
        
    file.close()


prefix = 'https://onlinelibrary-wiley-com.offcampus.lib.washington.edu/'

search_term = input("Input Wiley Online Library search term: ")
print('\n')
filename = input("Input filename with .txt extension you wish to store urls in: ")
print('\n')

driver = webdriver.Chrome()

master_list = []
years = np.arange(1990,2020)

for year in years:
    year = str(year)
    scraped_urls = scrape_all(search_term,driver,year)
    proxy_urls = proxify(scraped_urls,prefix)
    for link in proxy_urls:
        with open(filename,'a') as f:
            f.write(link)
            f.write('\n')
    for link in proxy_urls:
        master_list.append(link)
    print('Number of URLs collected = ',len(master_list))

write_urls(master_list,filename)

driver.quit()
