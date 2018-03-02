from __future__ import print_function
import urllib2
import bs4
import requests
from urlparse import urlparse
from urlparse import urljoin
import regex as re
from time import sleep
import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium
from selenium.webdriver.common.action_chains import ActionChains
import numpy
import datetime
import math
import csv



modelintercept = .051557
modelcoefficient1 = -0.003268



site= "https://www.hltv.org/matches?star=1"
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

# requests website
req = urllib2.Request(site, headers=hdr)


try:
    page = urllib2.urlopen(req)
    print('connection established')
except urllib2.HTTPError as e:
    print(e.fp.read())

content = page.read()

# html parser
sauce = bs4.BeautifulSoup(content, 'html.parser')
soup = sauce.body

# turns scores from html to text
soup = sauce.encode('utf-8')



# sorts for match links
x = sauce.find("div", {"class": "match-day"})

for url in x.find_all('a', href=re.compile("/matches/")):
    base_url = 'https://www.hltv.org'
    link = url.get('href')
    links = urljoin(base_url, link)
    Teamline = []
    if links.startswith("https://"):

        # takes absolute match links and extracts data
        try:
            r = requests.get(links)
            page = r.text
            littlesoup = bs4.BeautifulSoup(page, 'html.parser')

            littlesauce_names = littlesoup.find_all("div", {"class": "teamName"})
            names = re.sub('<[^>]+>', '', str(littlesauce_names))
            Teamline.append(names)


            team1 = littlesoup.find_all('a', href=re.compile("/team/+"))[1]
            team2 = littlesoup.find_all('a', href=re.compile("/team/+"))[2]

            # print(team1)
            # extracts relative team link from match page
            s = re.search(r'href="([^"]*)"', str(team1)).group(1)
            t = re.search(r'href="([^"]*)"', str(team2)).group(1)



            # converts to absolute
            team1_absolute = urljoin(base_url, s)
            team2_absolute = urljoin(base_url, t)
            differencelist = []

            if team1_absolute.startswith("https://"):

                driver = webdriver.Chrome('C:\Python27\chromedriver.exe')  # Optional argument, if not specified will search path.

                mofo = driver.get(team1_absolute)
                sauce = driver.page_source.encode('utf-8')
                h = re.search(r'/teams">#([^"]*)</a', str(sauce))
                Teamline.append(h.group(1))

                driver.quit()

            if team2_absolute.startswith("https://"):

                driver = webdriver.Chrome('C:\Python27\chromedriver.exe')  # Optional argument, if not specified will search path.

                mofo = driver.get(team2_absolute)
                sauce = driver.page_source.encode('utf-8')
                h = re.search(r'/teams">#([^"]*)</a', str(sauce))
                Teamline.append(h.group(1))

                driver.quit()

            pred_comp = modelintercept + modelcoefficient1*(float(differencelist[0])-float(differencelist[1]))
            actualpred = math.exp(pred_comp)/(1 + math.exp(pred_comp))

            Teamline.append(actualpred)
            Teamline.append((float(differencelist[0])-float(differencelist[1])))
            print(Teamline)
            with open('csvfile.csv', 'wb') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow(Teamline)

        except IndexError:
            pass
