import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import random
from time import sleep

#Chrome WebDriver
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
browser.set_page_load_timeout(60)
wait = WebDriverWait(browser, 20)


products = []

# To scrape a single page for product details and links
def scrape_page(url, product_type):
    try:
        browser.get(url)
        sleep(random.uniform(2, 10))
        html_source_code = browser.execute_script("return document.body.innerHTML;")
        html_soup = BeautifulSoup(html_source_code, "html.parser")
        
        
        product_containers = html_soup.find_all("div", {"data-component-type": "s-search-result"})
        
        for container in product_containers:
            if len(products) >= 1000:
                return  

            
            name_tag = container.find("span", class_="a-size-base-plus a-color-base a-text-normal")
            name = name_tag.text.strip() if name_tag else "No Title"
            
            price_tag = container.find("span", class_="a-price-whole")
            price = price_tag.text.strip() if price_tag else "NULL"
            
            link_tag = container.find("a", class_="a-link-normal s-no-outline")
            link = "https://www.amazon.in" + link_tag['href'] if link_tag else "No Link"
            
            products.append({"Product Name": name, "Product Price": price, "Product Link": link, "Product Type": product_type, "Category": "Skin care"})
    
    except Exception as e:
        print(f"Error scraping page {url}: {e}")

# To scrape ingredients from a product page
def scrape_ingredients(url):
    try:
        browser.get(url)
        sleep(random.uniform(2, 10))
        html_source_code = browser.execute_script("return document.body.innerHTML;")
        html_soup = BeautifulSoup(html_source_code, "html.parser")
        
        
        important_info_div = html_soup.find("div", id="important-information")
        
        if important_info_div:
            
            content_divs = important_info_div.find_all("div", class_="a-section content")
            
            for content_div in content_divs:
                ingredients_header = content_div.find("h4", string=lambda text: "Ingredients:" in text)
                
                if ingredients_header:
                    ingredients_list = content_div.find_all("p")
                    
                    ingredients = ", ".join([p.get_text(strip=True) for p in ingredients_list if p.get_text(strip=True)])
                    return ingredients if ingredients else "NULL"
                    
    except Exception as e:
        print(f"Error scraping ingredients from {url}: {e}")
    
    return "NULL"

# URLs for different skin care product types
urls = {
    "Face Serum": "https://www.amazon.in/s?k=face+serum&rh=n%3A1374407031&ref=nb_sb_noss",
    "Face Cleanser - Milk Based": "https://www.amazon.in/s?k=face+cleanser+-+milk+based&rh=n%3A1374414031&ref=nb_sb_noss",
    "Face Cleanser - Water Based": "https://www.amazon.in/s?k=face+cleanser+-+water+based&rh=n%3A1374414031&ref=nb_sb_noss",
    "Face Cream - Day creams": "https://www.amazon.in/s?k=face+cream+-+day&rh=n%3A1374414031&ref=nb_sb_noss",
    "Face Cream - Night Cream": "https://www.amazon.in/s?k=face+cream+-+night+cream&rh=n%3A1374414031&ref=nb_sb_noss",
    "Sunscreen": "https://www.amazon.in/s?k=sunscreen&rh=n%3A1374407031&ref=nb_sb_noss",
    "Toner": "https://www.amazon.in/s?k=toner&i=beauty&rh=n%3A1374407031&qid=1718684023&ref=sr_pg_1",
    "Face Wash": "https://www.amazon.in/s?k=face+wash&rh=n%3A1374407031&ref=nb_sb_noss",
    "Face Oil": "https://www.amazon.in/s?k=face+oil&rh=n%3A1374407031&ref=nb_sb_noss"
    
}


for product_type, url in urls.items():
    for pg_index in range(1, 3):  
        if len(products) >= 1000:
            break  
        page_url = f"{url}&page={pg_index}"
        scrape_page(page_url, product_type)

for product in products:
    if product["Product Link"] != "No Link":
        product["Ingredients"] = scrape_ingredients(product["Product Link"])
    else:
        product["Ingredients"] = "NULL"

browser.quit()

# Converting the list of dictionaries to a DataFrame and save it to a CSV file
df = pd.DataFrame(products)
df.to_csv('product_details.csv', index=False)


print("Number of columns:", df.shape[1])
print(df.head())
