from __init__ import *


for vehicle in vehicle_types:
    browser = get_browser(maximized=False)
    df = pd.read_csv(f'../{vehicle}/models.csv')

    links = df['model_link'].tolist()
    model = df['model'].tolist()
    brand = df['brand'].tolist()

    all_brands = []
    all_models = []
    all_links = []
    all_variants = []
    all_variants_links = []
    available = []


    for i in range(len(df)):
        browser.get(links[i])
        try:
            collect_variant_information(i, browser, all_brands, all_models, all_links,
                                        all_variants, all_variants_links, available, brand, model, links)
        except TimeoutException:
            logger.debug(f'There are no variants for {
                brand[i]} {model[i]} available')
            all_brands.append(brand[i])
            all_links.append(links[i])
            all_models.append(model[i])
            all_variants.append('N/A')
            all_variants_links.append(links[i])
            available.append(0)
    df = pd.DataFrame({
        'brand': all_brands,
        'model': all_models,
        'model_link': all_links,
        'variant': all_variants,
        'variant_link': all_variants_links,
        'available': available
    })

    browser.quit()

    if not os.path.exists(vehicle):
        os.makedirs(vehicle)
    df.to_csv(f'../{vehicle}/variants.csv', index=False)
    logger.info(f'Saved {vehicle} variants to {vehicle}/variants.csv')
    
    time.sleep(5)
