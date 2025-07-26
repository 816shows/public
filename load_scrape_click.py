"""
script to perform browser automation to load page and scrape, then click next page to maxclicks
"""


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time


def page_then_click(maxclicks):
    url = "https://r.yogaalliance.org/SchoolProfileReviews?sid=2742"
    click_count = 0
    # Set up Firefox WebDriver
    firefox_options = Options()
    firefox_options.headless = True
    service = Service('/usr/local/bin/geckodriver')
    driver = webdriver.Firefox(service=service, options=firefox_options)

    # Load the webpage & wait for full content
    driver.get(url)
    time.sleep(2)

    # Loop to find button, dump page content into soup, scrape details, then click
    try:
        WebDriverWait(driver, 2).until(
             EC.element_to_be_clickable((By.ID, 'dnn_ctr1756_View_RdpSchoolReviews_ctl02_NextButton'))
        )

        while click_count < maxclicks:
            time.sleep(5)

            # Begin logic for web scraping
            soup = BeautifulSoup(driver.page_source, "html.parser")
            target_element = soup.find('ul', class_='ya-review-block')

            if target_element:
                reviews = target_element.find_all('li', class_='ya-first-item')
                for review in reviews:
                    # Find the 'ya-review-feedback-info' div first
                    feedback_info = review.find('div', class_='ya-review-feedback-info')
                    if feedback_info:
                        # Then find all 'ya-row' divs within 'feedback_info'
                        ya_rows = feedback_info.find_all('div', class_='ya-row')
                        # The second 'ya-row' (index 1) contains the reviewer's name
                        if len(ya_rows) > 1:
                            reviewer_div = ya_rows[1]
                            reviewer_text = reviewer_div.text.strip()
                            print(reviewer_text)   # alternatively this could be added to a list, further formatted, etc.
                        else:
                            print("Could not find the expected 'ya-row' div for reviewer.")
                    else:
                        print("Could not find 'ya-review-feedback-info' div.")
            else:
                print("Target element not found")

            try:
                # Try to locate and click using By.ID CSS Selector
                next_button = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.ID, 'dnn_ctr1756_View_RdpSchoolReviews_ctl02_NextButton'))
                )
                # Attempt a standard Selenium click first
                if next_button.is_displayed() and next_button.is_enabled():
                    next_button.click()
                    print(f"Clicked 'NextButton' using standard Selenium click. Click count: {click_count + 1}")
                else:
                    # If not displayed/enabled for standard click, immediately try JS
                    raise Exception("NextButton not directly clickable, attempting JS click.")

            except Exception as e:
                print(f"Standard Selenium click failed: {e}. Attempting JavaScript click for robustness.")
                try:
                    # Fallback to JavaScript click, confirming element presence
                    next_button_js = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'dnn_ctr1756_View_RdpSchoolReviews_ctl02_NextButton'))
                    )
                    driver.execute_script("arguments[0].click();", next_button_js)
                    print(f"Clicked 'NextButton' using JavaScript executor (fallback). Click count: {click_count + 1}")

                except Exception as js_e:
                    print(f"JavaScript click (fallback) also failed: {js_e}. Breaking loop.")
                    break # Exit the loop if even the JavaScript click fails

            click_count += 1

    except:
        print("No more 'Next' button or not clickable. End of pages.")

    finally:
        driver.quit()


if __name__ == "__main__":
    page_then_click(2)
