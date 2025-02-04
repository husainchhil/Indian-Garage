from __init__ import *


for vehicle in vehicle_types:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    logger.info(f'Fetching {vehicle} models')
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(f"https://www.zigwheels.com/new{vehicle}s")

    df = get_model_data(browser)
    df.to_csv(f'../{vehicle}/models.csv', index=False)
    browser.quit()
    logger.info(f'Saved {vehicle} models to {vehicle}/models.csv')
    time.sleep(5)