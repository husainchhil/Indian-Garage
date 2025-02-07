from __init__ import *


for vehicle in vehicle_types:
    browser = get_browser(maximized=False)
    df = pd.read_csv(f'{vehicle}/variants.csv')
    logger.info(f"Starting to fetch specs for {vehicle}s")

    data = {}
    num_brands = len(df['brand'].unique()[:])

    for h in range(num_brands):
        brand = df['brand'].unique()[h]
        data[brand] = {}

        brand_models = df[df['brand'] == brand]['model'].unique()[:]
        num_models = len(brand_models)

        for model in brand_models:
            data[brand][model] = {}

            model_variants = df[(df['brand'] == brand) &
                                (df['model'] == model)][:]
            num_variants = len(model_variants)

            for i, row in model_variants.iterrows():
                try:

                    variant = row['variant']
                    variant_link = row['variant_link']
                    available = row['available']

                    logger.info(f"Fetching specs for {
                                brand} {model} {variant}")

                    browser.get(variant_link)
                except Exception as e:
                    logger.error(f"Error fetching specs for {variant}! {
                        str(e).splitlines()[0]}")
                    num_variants -= 1
                    logger.info(f"Remaining brands: {num_brands}, models in {brand}: {
                                num_models}, variants in {model}: {num_variants}\n")
                    continue
                try:
                    desc = browser.find_element(
                        By.CSS_SELECTOR, 'div.fnt-14.read-more.mx-ht-pg-desc.rm p').get_attribute('innerText').strip()
                except Exception as e:
                    logger.error(f"Description not found for {
                        variant}! {str(e).splitlines()[0]}")
                    desc = None

                try:
                    exshowroom_price = browser.find_element(
                        By.CSS_SELECTOR, 'ul.pl-15.pr-15.fnt-14.simple-list li > span').get_attribute('innerText')
                except Exception as e:
                    logger.error(
                        f"Error fetching ex-showroom price for {variant}! {str(e).splitlines()[0]}")
                    exshowroom_price = None

                try:
                    specs = webdriver_wait(
                        browser, 'div[class="spec-t-ctr"]', multiple=True)
                except Exception as e:
                    logger.error(f"Specs not found for {variant}! {
                        str(e).splitlines()[0]}")
                    specs = []

                data[brand][model][variant] = {}
                for j in range(len(specs)):
                    try:
                        table_rows = webdriver_wait(
                            specs[j], 'td', multiple=True)
                        spec = specs[j].text.split('\n')[0]
                        data[brand][model][variant][spec] = {}

                        for k in range(0, len(table_rows), 2):
                            try:
                                key = table_rows[k].get_attribute(
                                    'innerText').strip()
                                value = table_rows[k+1].get_attribute(
                                    'innerText').strip().replace('\n...Read More', '').strip()
                                data[brand][model][variant][spec][key] = value
                            except Exception as e:
                                logger.error(
                                    f"Error fetching key-value pair for {variant}! {str(e).splitlines()[0]}")
                        logger.debug(
                            f"Added {specs[j].text.split('\n')[0]}")
                    except Exception as e:
                        logger.error(f"Error processing spec for {
                            variant}! {str(e).splitlines()[0]}")

                data[brand][model][variant]['URL'] = variant_link
                logger.debug(f"Added URL")

                data[brand][model][variant]['Description'] = desc
                logger.debug(f"Added description")

                data[brand][model][variant]['Ex-showroom Price'] = exshowroom_price
                logger.debug(f"Added ex-showroom price")

                data[brand][model][variant]['Available'] = True if available else False

                logger.success(f"Completed fetching specs for {
                    brand} {model} {variant}")
                num_variants -= 1
                logger.info(f"Remaining brands: {num_brands}, models in {brand}: {
                            num_models}, variants in {model}: {num_variants}\n")

            num_models -= 1
        num_brands -= 1
    browser.quit()

    if not os.path.exists(vehicle):
        os.makedirs(vehicle)
    with open(f'{vehicle}/specs.json', 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)
    logger.success(f"Completed fetching specs. Saved to {vehicle}/specs.json")

    # sleep for 10 seconds to avoid getting blocked
    time.sleep(10)

data = {}
for vehicle in vehicle_types:
    with open(f'{vehicle}/specs.json', 'r') as f:
        data[vehicle.capitalize()] = json.load(f)

with open('data.json', 'w') as f:
    json.dump(data, f, indent=4, sort_keys=True)
