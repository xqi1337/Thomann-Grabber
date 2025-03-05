import requests
from bs4 import BeautifulSoup
import csv

def scrape_product_page(link):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(link, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"Successfully fetched product page: {link}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product title
        title_tag = soup.find("h1", class_="fx-product-headline")
        product_title = title_tag.text.strip() if title_tag else ""
        
        # Extract price
        price_tag = soup.find("div", class_="price")
        price = price_tag.text.strip().replace("€", "").replace(".", "").replace('▒', '') if price_tag else ""
        
        # Extract description
        description_tag = soup.find("div", class_="text-original")
        description = description_tag.text.strip() if description_tag else ""
        
        # Extract image links
        image_tags = soup.find_all("picture", class_="ZoomImagePicture")
        image_links = [img_tag['src'] for picture in image_tags if (img_tag := picture.find("img")) and 'src' in img_tag.attrs]
        
        # Extract brand
        brand = product_title.split()[0] if product_title else ""
        
        # Format data as WooCommerce compatible
        product_data = {
            "ID": "",
            "Type": "simple",
            "SKU": "",
            "Name": product_title,
            "Published": 1,
            "Is featured?": 0,
            "Visibility in catalog": "visible",
            "Short description": description,
            "Description": description,
            "Date sale price starts": "",
            "Date sale price ends": "",
            "Tax status": "taxable",
            "Tax class": "",
            "In stock?": 1,
            "Stock": "",
            "Low stock amount": "",
            "Backorders allowed?": 0,
            "Sold individually?": 0,
            "Weight (kg)": "",
            "Length (cm)": "",
            "Width (cm)": "",
            "Height (cm)": "",
            "Allow customer reviews?": 1,
            "Purchase note": "",
            "Sale price": "",
            "Regular price": price,
            "Categories": "",
            "Tags": "",
            "Shipping class": "",
            "Images": ",".join(image_links),
            "Download limit": "",
            "Download expiry days": "",
            "Parent": "",
            "Grouped products": "",
            "Upsells": "",
            "Cross-sells": "",
            "External URL": "",
            "Button text": "",
            "Position": 0,
            "Meta: _custom_field": "",
            "Attribute 1 name": "Marke",
            "Attribute 1 value(s)": brand,
            "Attribute 1 visible": 1,
            "Attribute 1 global": 1
        }
        
        return product_data
    
    except Exception as e:
        print(f"Error scraping product page {link}: {e}")
        return None

def save_to_csv(products_data, filename):
    if not products_data:
        print("No data to save.")
        return
    fieldnames = list(products_data[0].keys())
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for product_data in products_data:
                writer.writerow(product_data)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")

try:
    for i in range(1, 20):
        url = f"https://www.thomann.de/de/turntables.html?ls=25&pg={i}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            print(f"Successfully fetched page {i}")
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            product_links = soup.find_all("a", class_="product__content")
            links = [link['href'] for link in product_links if link and 'href' in link.attrs]
            print(f"Found {len(links)} products on page {i}")
            
            all_products_data = []  # Initialize a list to collect all product data for the current page
            
            for link in links:
                full_link = f"https://thomann.de/de/{link}"
                product_data = scrape_product_page(full_link)
                if product_data:
                    all_products_data.append(product_data)
            
            # Save all products from the current page to the CSV
            csv_filename = f'turntables{i}.csv'
            save_to_csv(all_products_data, filename=csv_filename)
            print(f"Page {i} processed successfully with {len(all_products_data)} products")
            
        except Exception as e:
            print(f"Error processing page {i}: {e}")

    print("Product data saved to CSV files.")
except Exception as e:
    print(f"An overall error occurred: {e}")
