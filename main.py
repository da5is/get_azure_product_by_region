from selenium import webdriver # pip install selenium
from pprint import pprint
from selenium.webdriver.common.by import By

def get_status_from_row(row):
    product = row.get_attribute("data-product-slug")
    status_cell = row.find_element(by=By.TAG_NAME, value='td')
    images = status_cell.find_elements(by=By.TAG_NAME, value="img")
    status = 'Not Available'
    if len(images) > 0:
        src = images[0].get_property('src')
        if 'ga.svg' in src:
            status = 'Generally Available'
        elif 'planned-active.svg' in src:
            status = 'Future Availability Planned'
        elif 'preview.svg' in src:
            status = 'Preview'
    return product, status

def get_products_by_region(region:str)->dict:
    services = {}
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument("--headless=new")  
    driver = webdriver.Chrome(options=options)

    driver.get(f"https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/?regions={region}&rar=true&products=all&cdn=disable")
    table = driver.find_element(by=By.ID, value='primary-table') # gets the JS rendered table
    status_rows = table.find_elements(by=By.TAG_NAME, value='tr')
    for row in status_rows:
        if row.get_attribute("class") == "service-row":
            product, status = get_status_from_row(row)
            services[product] = {
                    "name": product,
                    "status": status,
                    "capabilities": {}
                }
        if row.get_attribute("class") == "capability-row":
            capability, status = get_status_from_row(row)
            services[product]["capabilities"][capability] = status
    return(services)

def write_services_into_csv(region:str, region_product_data: dict):
    import csv
    expanded_services = []
    keys = sorted(region_product_data.keys())
    header = ["Service", "Capability", "Capability Status"]
    for key in keys:
        if not region_product_data[key]['capabilities']:
            expanded_services.append([region_product_data[key]['name'], "",region_product_data[key]['status']])
        else:
            capability_keys = sorted(region_product_data[key]['capabilities'].keys())
            for capability_key in capability_keys:
                expanded_services.append([region_product_data[key]['name'], capability_key, region_product_data[key]['capabilities'][capability_key]])
    with open(f'{region}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for value in expanded_services:
            writer.writerow(value)