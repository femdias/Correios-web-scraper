# -*- coding: utf-8 -*-

'''
In this code, we perform a web scraping of the Correios website, in order to get
the complete address of each of the zip codes (CEPs).
'''

import selenium
import pandas as pd
import numpy as np
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import ChromiumOptions
from webdriver_manager.chrome import ChromeDriverManager
import os
import tqdm

# Setting working directory
os.chdir(r'C:\Users\femdi\Documents\~Variados\Github\Correios web scraper')

# Import CEPs dataset (postal code)
ceps = pd.read_excel('sample.xlsx', dtype = str)

# Chromedriver installation (when needed)
chrome_options = ChromiumOptions()
#chrome_options.headless = True
#service = Service(ChromeDriverManager().install())

# Opening Chrome
driver = webdriver.Chrome(options=chrome_options)

# Opening Correios site
url = "https://buscacepinter.correios.com.br/app/endereco/index.php"
driver.get(url)

    
df_results = pd.DataFrame(columns = ["Address", "Neighborhood", "Municipality", "CEP"])
for i in tqdm.tqdm(ceps['CEP']):
    
    wait1 = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.NAME,'endereco')))

    # Finding the search bar
    barra_de_escrever = driver.find_element(By.NAME,'endereco')
    
    # Writing CEP and pressing enter
    barra_de_escrever.send_keys(i + "\n")
    
    
    # Finding and saving CEP data 
    try:
        #Waiting until the website loads complety (I chose to wait for the houses images because they are the last things to load)
        wait = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.TAG_NAME, "td")))
        
        # Find elements
        elements = driver.find_elements(By.TAG_NAME,'td')
        
        # Dictionary of data
        dict_elements =  dict([('Address',elements[0].text),
                                ('Neighborhood',elements[1].text),
                                ('Municipality',elements[2].text),
                                ('CEP',elements[3].text)])
        
    except: 
        # If error, we close the window, open again the page and try again
        # I think there is a barrier on the Correios html to prevent the used of 
        # web scraping. That is the way I found out to bypass this.
        try:
            # Reload page
            driver.quit()
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            wait1 = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.NAME,'endereco')))
            
            # Finding the search bar
            barra_de_escrever = driver.find_element(By.NAME,'endereco')
            
            # Writing CEP and pressing enter
            barra_de_escrever.send_keys(i + "\n")
            
            wait = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.TAG_NAME, "td")))
        
            # Find elements
            elements = driver.find_elements(By.TAG_NAME,'td')
            
            # Dictionary of data
            dict_elements =  dict([('Address',elements[0].text),
                                    ('Neighborhood',elements[1].text),
                                    ('Municipality',elements[2].text),
                                    ('CEP',elements[3].text)])
            

        # If there is no data               
        except:
            dict_elementos = dict([('Address', 'No Info'),
                                    ('Neighborhood', 'No Info'),
                                    ('Municipality', 'No Info'),
                                    ('CEP', i)])
            

    # Adding to results dataset
    df_results = pd.concat([df_results, pd.DataFrame.from_dict(dict_elements, 
                                            orient = 'index').T], axis = 'rows')
    
    # Going back to the previous page
    driver.get(url)
    

df_results = df_results.drop_duplicates().reset_index(drop = True)
df_results.to_excel(r"sample_with_address.xlsx", index = False)



