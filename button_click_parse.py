# script to load a web page, click the Load More button to populate the HTML content, then scrape its details

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


def load_more(load_more_selector, max_clicks=3):
    """set up the web driver, load the page, click the page the number of times specified, gather the contents
       of the page into an object to be passed to the parsing function
    """
    try:
        # Set up Firefox WebDriver
        firefox_options = Options()
        firefox_options.headless = True  # Run Firefox in headless mode (no GUI)
        service = Service('/usr/local/bin/geckodriver')  # Path to GeckoDriver executable
        driver = webdriver.Firefox(service=service, options=firefox_options)

        # URL of the website to scrape
        url = "https://us.smartprix.com/mobiles"

        # Load the webpage & wait for initial base content
        driver.get(url)
        time.sleep(2)

        # Loop to click the Load More button
        try:
            click_count = 0
            while click_count < max_clicks:
                # Wait for the "Load More" button to be clickable
                try:
                    load_more_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, f'.{load_more_selector}'))
                    )
                    load_more_button.click()
                    time.sleep(2)  # Wait for new page content to load (adjust as needed)
                    click_count += 1

                except Exception:
                    break

            soup = BeautifulSoup(driver.page_source, "html.parser")
            return soup

        except Exception as e:
            print(f"An error occurred during the clicking loop: {e}")

    except Exception as e:
        print(f"An error occurred during browser setup or initial load: {e}")

    finally:
        driver.quit()  # Close the browser


def scrape_data(soup):
    """logic to parse the details from the HTML collected in the first function"""
    # Find the target element containing the items
    target_element = soup.find('div', class_='sm-box')

    if target_element:
        # Find item tiles
        tiles = soup.select('div.sm-product.has-tag.has-features.has-actions')
        if not tiles:
            print(f"No tiles found for page")

        for tile in tiles:
            item_name_tag = tile.find('h2')
            if item_name_tag:
                item_name = item_name_tag.text.strip()
                cost_tag = tile.find('span', class_='price')
                cost = cost_tag.text.strip()
                print(f"Item name: {item_name} Cost: {cost}")


if __name__ == "__main__":
    load_more_selector = "sm-load-more"
    payload = load_more(load_more_selector)
    scrape_data(payload)
