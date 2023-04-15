# Description: This script will compare the staging and production page source
# Author: Clark Medina
# For GEL Team
import pandas as pd
import requests
import time
import bs4
import os
import collections
# read the urls from the file
urls=pd.read_csv('urls.csv')
results = pd.DataFrame(columns=['Staging', 'Production', 'Status'])
# check if staging and production dirs exist
if not os.path.exists('staging'):
    os.makedirs('staging')
if not os.path.exists('production'):    
    os.makedirs('production')   

# loop through the rows
for index, row in urls.iterrows():
    # get staging url   
    url=row['Staging']
    # get production url
    prod_url=row['Production']
    time.sleep(3)
    try:
        print("Checking " + url)
        # open staging url  
        r=requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code != 200:
            print("Error: please ensure this page is on stg for " + url)
            results.loc[index] = {'Staging': url, 'Production': prod_url, 'Status': 'Not on Staging'}
        
        # save the staging page source
        staging_page_source = r.text
        with open('staging/' + url.replace('/','_') + '.html', 'w') as f:
            f.write(r.text)
        # get all the links on the staging page
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        links = soup.find_all('a')
        page_links = []
        for link in links:
            # get the href attribute
            href = link.get('href')
            # if the href attribute is not empty and starts with http and contains the staging url
            if href and href.startswith('http') and href.find(url) != -1:
                # add the link to the list
                page_links.append(href)
        # loop through the links
        for link in page_links:
            # open the link
            r=requests.get(link,headers={'User-Agent': 'Mozilla/5.0'})
            time.sleep(3)
            if r.status_code==200:
                # save the page source to a file in staging dir
                with open('staging/' + link.replace('/','_') + '.html', 'w') as f:
                    f.write(r.text) 
    except:
        print("Error: please ensure this page is on stg for " + url)
        results.loc[index] = {'Staging': url, 'Production': prod_url, 'Status': 'Not on Staging'}
        continue
    time.sleep(3)
    try:
        print("Checking " + prod_url)
        # open production url
        r=requests.get(prod_url,headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code != 200:
            print("Error: please ensure this page is on prod for " + url)
            results.loc[index] = {'Staging': url, 'Production': prod_url, 'Status': 'Not on Production'}
        # save the production page source
        production_page_source = r.text
        with open('production/' + prod_url.replace('/','_') + '.html', 'w') as f:
            f.write(r.text)
        # get all the links on the production page
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        links = soup.find_all('a')
        page_links = []
        for link in links:
            r=requests.get(link,headers={'User-Agent': 'Mozilla/5.0'})
            time.sleep(3)
            # get the href attribute
            href = link.get('href')
            # if the href attribute is not empty and starts with http and contains the production url
            if href and href.startswith('http') and href.find(prod_url) != -1:
                # add the link to the list
                page_links.append(href)
        # loop through the links
        for link in page_links:
            # open the link
            r=requests.get(link,headers={'User-Agent': 'Mozilla/5.0'})
            time.sleep(3)
            if r.status_code==200:
                # save the page source to a file in production dir
                with open('production/' + link.replace('/','_') + '.html', 'w') as f:
                    f.write(r.text)
    except:
        print("Error: please ensure this page is on prod for " + url)
        results.loc[index] = {'Staging': url, 'Production': prod_url, 'Status': 'Not on Production'}

    # compare the files in staging and production dirs
    staging_files = os.listdir('staging')
    production_files = os.listdir('production')
    staging_files.sort()
    production_files.sort()
    
    # create products of production and staging files using collections
    #products = collections.product(staging_files, production_files)
    # loop through the products
    for product in products:
        # open the files
        with open('staging/' + product[0], 'r') as f1:
            with open('production/' + product[1], 'r') as f2:
                # compare the files
                if f1.read() == f2.read():
                    results.loc[index] = {'Staging': url, 'Production': prod_url, 'Status': 'Match'}
                else:
                    results.loc[index] = {'Staging': url, 'Production': prod_url, 'Status': 'Not Match'}

    # clear the staging and production dirs
    for file in staging_files:
        os.remove('staging/' + file)
    for file in production_files:
        os.remove('production/' + file)
# save the result to a csv file
results.to_csv('results.csv')
