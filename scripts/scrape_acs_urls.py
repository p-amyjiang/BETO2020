import selenium
from selenium import webdriver
import numpy as np
import pandas as pd
import bs4
from bs4 import BeautifulSoup
import time

"""
This code is used to scrape ScienceDirect of publication urls and write them to
a text file in the current directory for later use.

To use this code, go to ScienceDirect.com and search for the topic of interest.
Then, copy the URL and paste it into terminal when prompted for user input.

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

def build_annual_urls(search_term,max_pages):
    """
    This method takes the first SD url and creates a list of
    urls which lead to the following pages on SD which will be
    scraped. The page list is for a given year.
    """
    first_url = 'https://pubs.acs.org/action/doSearch?AllField=' + search_term.replace(" ", "+") + '&startPage=0&pageSize=100'
    
    page_urls = [first_url]
    for i in range(max_pages-1):
        urli = first_url.replace("startPage=0", "startPage=" + str(i))
        page_urls.append(urli)

    return page_urls

def scrape_all(first_url,driver,max_pages):
    """
    This method takes the first ScienceDirect url and navigates
    through all 60 pages of listed publications, scraping each url
    on each page. Returns a list of the urls. Scrapes all urls for a given year.
    """
    page_list = build_annual_urls(first_url,max_pages)
    urls = []
    for page in page_list:
        driver.get(page)
        time.sleep(1) #must sleep to allow page to load
        elems = scrape_page(driver)
        links = clean(elems)
        if len(links) < 2:
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
        sd_id = url[21:]
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



driver = webdriver.Chrome()
prefix = 'https://pubs-acs-org.offcampus.lib.washington.edu/'

search_term = input("Input ACS search term: ")
print('\n')
filename = input("Input filename with .txt extension you wish to store urls in: ")
print('\n')
max_pages = int(input("Input maximum number of pages to scrape: "))

master_list = []

scraped_urls = scrape_all(search_term,driver,max_pages)
proxy_urls = proxify(scraped_urls,prefix)
for link in proxy_urls:
    master_list.append(link)
print('Number of URLs collected = ',len(master_list))

write_urls(master_list,filename)

driver.quit()
