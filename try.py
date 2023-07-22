import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Function to scrape product listing page and extract required data
def scrape_product_listing(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    products = soup.find_all("div", {"data-component-type": "s-search-result"})

    data = []
    for product in products:
        product_url = "https://www.amazon.in" + product.find("a", {"class": "a-link-normal"})["href"]

        # Handle error if the product name is not found
        product_name_elem = product.find("span", {"class": "a-size-medium a-color-base a-text-normal"})
        product_name = product_name_elem.text.strip() if product_name_elem else "N/A"       
       
       
        # Handle error if the product price is not found
        product_price_elem = product.find("span", {"class": "a-offscreen"})
        result_price = product_price_elem.text.strip() if product_price_elem else "N/A"
        numeric_str = result_price.replace('₹', '').replace(',', '')
        product_price = int(numeric_str)

        # Handle error if the product rating is not found
        product_rating_elem = product.find("span", {"class": "a-icon-alt"})
        product_rating = product_rating_elem.text.strip().split()[0] if product_rating_elem else "N/A"

        # Handle error if the number of reviews is not found
        product_reviews_elem = product.find("span", {"class": "a-size-base"})
        product_reviews = product_reviews_elem.text.strip() if product_reviews_elem else "N/A"

        data.append({
            "Product URL": product_url,
            "Product Name": product_name,
            "Product Price": product_price,
            "Rating": product_rating,
            "Number of reviews": product_reviews,
        })

    return data

def product_description_conversion(product_description_elem):
    product_description = ""
    for element in product_description_elem:
        product_description += element.text.strip() + "\n"

    result = product_description.strip()
    sorted_reviews_index = result.find("Sort reviews by")
    if sorted_reviews_index != -1:
        result = result[:sorted_reviews_index]
        product_description = " ".join(result.strip().split())
    return product_description    

# Function to scrape product page and extract additional information
def scrape_product_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    description_elem = soup.find("span", {"id": "productTitle"})
    description = description_elem.text.strip() if description_elem else "N/A"

    asin_elem = soup.find("input", {"name": "ASIN"})
    asin = asin_elem["value"] if asin_elem else "N/A"

    product_description_elem =soup.find_all("span", {"class": "a-list-item"})

    product_description = product_description_conversion(product_description_elem) if product_description_elem else "N/A"

    manufacturer_elem = soup.find("a", {"id": "bylineInfo"})
    manufacturer = manufacturer_elem.text.strip() if manufacturer_elem else "N/A"

    return {
        "Description": description,
        "ASIN": asin,
        "Product Description": product_description,
        "Manufacturer": manufacturer
    }

# Main function to scrape and save data in CSV
def main():
    base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
    pages_to_scrape = 20
    data = []

    # Scrape product listing pages
    for page_num in range(1, pages_to_scrape + 1):
        url = base_url + str(page_num)
        data += scrape_product_listing(url)

    print("scrape_product_listing Done!...")    

    # Scrape additional information from each product page
    for i, item in enumerate(data):
        product_url = item["Product URL"]
        additional_info = scrape_product_page(product_url)
        data[i].update(additional_info)
    print("scrape_product_page Done!...")    
    # Save data in CSV format
    headers = ["Product URL", "Product Name", "Product Price", "Rating", "Number of reviews","Description", "ASIN", "Product Description", "Manufacturer"]
    with open("amazon_product_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    main()
