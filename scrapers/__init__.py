import os
import time
import json
import pandas as pd
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

vehicle_types = ['car', 'bike']


def get_browser(maximized=False):
    chrome_options = Options()
    if maximized:
        chrome_options.add_argument("--start-maximized")
    else:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    return webdriver.Chrome(options=chrome_options)


def webdriver_wait(browser, selector,  timeout=5, by=By.CSS_SELECTOR, multiple=False):
    element = WebDriverWait(browser, timeout).until(ec.presence_of_element_located(
        (by, selector)) if not multiple else ec.presence_of_all_elements_located((by, selector)))
    return element


def get_model_data(browser):


    df = pd.DataFrame(columns=['brand', 'model', 'model_link'])
    brands = webdriver_wait(browser, 'manufacturers', by=By.ID)
    brand_links = [link.get_attribute(
        'href') for link in brands.find_elements(By.TAG_NAME, 'a')]
    brand_names = [link.get_attribute('innerText').lower()
                   for link in brands.find_elements(By.TAG_NAME, 'a')]

    for i in range(1, len(brand_names)+1):
        attempts = 5
        while attempts > 0:
            try:
                logger.info(f'Selecting brand index {brand_names[i-1]}')
                makes = Select(webdriver_wait(
                    browser, selector='byBrandMake', by=By.ID))
                makes.select_by_index(i)
                time.sleep(1)
                models = Select(webdriver_wait(
                    browser, selector='byBrandModel', by=By.ID))
                model_names = [option.get_attribute(
                    'innerText').lower() for option in models.options[1:]]
                model_links = [
                    f'{brand_links[i-1]}/{option.get_attribute("data-url")}' for option in models.options[1:]]

                # add to the dataframe
                for j in range(len(model_names)):
                    new_row = pd.DataFrame([{'brand': brand_names[i-1], 'model': model_names[j],
                                            'model_link': model_links[j]}])
                    df = pd.concat([df, new_row], ignore_index=True)

                logger.info(f'Fetched {len(model_names)} models for brand {brand_names[i-1]}\n')
                break
            except Exception as e:
                attempts -= 1
                if attempts == 0:
                    logger.error(f'Exception encountered. Exiting...\n')
                    raise e
                logger.warning(f'{type(e).__name__} encountered. Retrying... Attempts left: {attempts}\n')
                time.sleep(2)

    df['model_link'] = df['model_link'].str.replace('-scooters', '-bikes')
    
    return df

def collect_variant_information(i, browser, all_brands, all_models, all_links, all_variants, all_variants_links, available, brand, model, links):

    try:
        variant_elements = webdriver_wait(
            browser, 'a[data-track-label="variant-widget"]', multiple=True)
        variants = [var.get_attribute('innerText').lower().replace(brand[i], '').replace(model[i], '').strip()
                    for var in variant_elements]
        variants_links = [var.get_attribute('href')
                          for var in variant_elements]
    except Exception as e:
        logger.error(f"Error fetching variants for {
                     model[i]}! {str(e).splitlines()[0]}")
        variants = []
        variants_links = []

    all_brands.extend([brand[i]] * len(variants))
    all_models.extend([model[i]] * len(variants))
    all_links.extend([links[i]] * len(variants))
    all_variants.extend(variants)
    all_variants_links.extend(variants_links)
    available.extend([1] * len(variants))
    logger.info(f'Added {len(variants)} variants for {
        brand[i]} {model[i]}')

