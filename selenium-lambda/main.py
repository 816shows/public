import os
import time
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException


def normalize_date(date_str):
    try:
        # Attempt to parse from original "Fri 30 Aug" format
        dt = datetime.strptime(date_str, "%a %d %b")
        return dt.strftime("%b %-d")
    except ValueError:
        return "N/A"


def find_events(url, element_id):
    """
    Extracts show names from a webpage using Selenium and BeautifulSoup,
    configured for a native headless environment within a Docker container.
    """
    driver = None  # Initialize driver to None for the finally block
    try:
        # Set up Firefox WebDriver.
        firefox_options = Options()

        # This is the key to running Firefox in native headless mode
        firefox_options.add_argument("--headless")

        firefox_options.add_argument("--disable-gpu")
        firefox_options.add_argument("--window-size=1920x1080")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")

        # Final fix for sandbox issues: set the security preference directly
        firefox_options.set_preference("security.sandbox.content.level", 0)

        # Set the profile directory to a writable location
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference("browser.download.dir", "/tmp")
        firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")

        # This is a critical step for the Lambda environment
        os.environ['HOME'] = '/tmp'

        # Configure the geckodriver service to log directly to stdout
        service = Service(service_log_path="geckodriver.log")
        service.log_output = sys.stdout

        driver = webdriver.Firefox(service=service, options=firefox_options)

        # Load the webpage
        driver.get(url)
        time.sleep(4)

        # Get the entire contents of the webpage
        page_content = driver.page_source

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_content, 'html.parser')

        # Find the specified element
        # Changed id to class for the dice-widget
        target_element = soup.find("div", class_=element_id)

        if target_element:
            # Find all <article> elements
            events = target_element.find_all('article')

            # Prepare list to store events data for CSV writing
            events_list = []

            # Iterate through events to extract show names and times
            for event in events:
                show_name = 'N/A'
                show_time = 'N/A'
                show_date = 'N/A'

                # Find the <a> element for show name
                show_name_element = event.find('a', class_='dice_event-title')
                if show_name_element:
                    show_name = show_name_element.text.strip()

                # Find the <time> element for extended show time
                show_when_element = event.find('time')
                if show_when_element:
                    show_long = show_when_element.text.strip()

                    # Split event date and time using Unicode character '―'
                    date_time_parts = show_long.split('―')

                    date_long = date_time_parts[0].strip() if len(date_time_parts) > 0 else "N/A"
                    try:
                        show_time12 = date_time_parts[1].strip()
                        show_time = datetime.strptime(show_time12, "%I:%M%p").strftime("%-I:%M %p")
                    except (IndexError, ValueError) as err:
                        print(f"Error parsing time from '{show_long}': {err}")
                        pass

                    # Normalize show date
                    show_date = normalize_date(date_long)

                # Append show info to list
                event_data = {'Location': 'minibar', 'Event': show_name, 'Date': show_date, 'Show Time': show_time}
                events_list.append(event_data)

            return events_list

        else:
            print(f"Element with class '{element_id}' not found on the page.")
            return []

    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    finally:
        # Quit the WebDriver
        if driver:
            driver.quit()


def handler(event, context):
    url = "https://www.minibarkc.com/tickets"
    element_id = "dice-widget"
    result = find_events(url, element_id)
    if result:
        print(result)
        return {
            'statusCode': 200,
            'body': result
        }
    else:
        return {
            'statusCode': 404,
            'body': 'No events found.'
        }
