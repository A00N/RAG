from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time
import json
import re

CHROMEDRIVER_PATH = "C:/webdrivers/chromedriver.exe"


def chrome_setup(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # Run in headless mode
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scroll_down(driver):
    time.sleep(4)
    button = driver.find_element(By.CSS_SELECTOR, '.css-47sehv')
    button.click()
     
    for _ in range(10): 
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        try:
            button = driver.find_element(By.CSS_SELECTOR, '.button.showmore')
            button.click()
        except:
            pass
        time.sleep(2)

def scrape_lunch(url):
    driver = chrome_setup()
    driver.get(url)
    scroll_down(driver)
    
    parent_elements = driver.find_elements(By.CSS_SELECTOR, ".item-container.masonry.isotope")

    for parent in parent_elements:

        # Restaurant name
        restaurant_name = parent.find_elements(By.TAG_NAME, "h3")
        names = [element.text for element in restaurant_name]

        #Bodies
        bodies = parent.find_elements(By.CSS_SELECTOR, ".item-body")
        in_bodies = [element for element in bodies]

        menu_items = []
        # Subitems in bodies
        for item in in_bodies:
            menus = item.find_elements(By.CSS_SELECTOR, ".menu-item")
            sep_menus = [element for element in menus]

            dish_prop = []
            for i in sep_menus:
                try:
                    dishes = i.find_elements(By.CSS_SELECTOR, ".dish")
                    name = [element.text for element in dishes]
                except:
                    name = "Unknown"

                try:
                    prices = i.find_elements(By.CSS_SELECTOR, ".price")
                    price = [element.text for element in prices]
                except:
                    price = "Unknown"

                try:
                    infos = i.find_elements(By.CSS_SELECTOR, ".info")
                    info = [element.text for element in infos]
                except:
                    info = "Unknown"

                if len(name) == 0:
                    name = "Unkown"
                if len(price) == 0:
                    price = "Unkown"
                if len(info) == 0:
                    info = "Unkown"

                dish_prop.append((name, price, info))
            menu_items.append(dish_prop)
    driver.quit()
    return list(zip(names, menu_items))

def write_json(data):
    json_data = {}
    for restaurant, items in data:
        json_data[restaurant] = [
            {
                "name": item[0][0],
                "price": item[1][0],
                "info": item[2][0]
            }
            for item in items
        ]
    json_string = json.dumps(json_data, ensure_ascii=False, indent=2)
    with open('menu_data.json', 'w', encoding='utf-8') as f:
        f.write(json_string)
    print("Succesfully wrote data to file")

if __name__ == "__main__":
    url = "https://www.lounaat.info/"
    data = scrape_lunch(url)
    write_json(data)
    

        

