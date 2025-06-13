import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


def rotate_url(base_url):
    """
    function to use the primary URL and rotate the "offset" for each page listing the next hundred riders
    loops through the total pagecount (defined by variable) to capture the full total of 1864 riders
    """
    anchor_url = base_url
    pagecount = 19
    for n in range(pagecount):
        offset = (n*100)
        url = anchor_url + f"&offset={offset}&teamlevel=&filter=Filter&p=me&s=uci-season-individual"
        extract_info(url)


def extract_info(url):
    """
    the actual scraping logic extracting the rider & points values from each row in the table
    will be called whatever number of times the total pagecount from rotate_url function
    writes to global list ranking[]
    """
    try:
        # Set up Firefox WebDriver
        firefox_options = Options()
        firefox_options.headless = True
        service = Service('/usr/local/bin/geckodriver')  # Path to GeckoDriver executable
        driver = webdriver.Firefox(service=service, options=firefox_options)

        # Load the webpage
        driver.get(url)

        # Wait for 4 seconds for the page to fully load
        time.sleep(4)

        # Get the entire contents of the webpage
        page_content = driver.page_source

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_content, 'html.parser')

        # Find the Table element
        target_element = soup.find("table", class_="basic")

        if target_element:
            # Find all <tr> elements
            riders = target_element.find_all('tr')

            # Iterate through rows to pull the rider & points details
            for rider in riders:
                try:
                    name_element = rider.find('a')   # first <a> element in the row so find is sufficient
                    name = name_element.text.strip()

                    if name:
                        point_element = rider.find_all('a')[2]    # third <a> element in the row so offset necessary
                        points = point_element.text.strip()
                        ranking.append((name, points))

                except AttributeError:
                    pass

            return ranking

        else:
            print("Target element not found")
            return None

    finally:
        # Quit the WebDriver
        driver.quit()


if __name__ == "__main__":
    ranking = []   # Initialize a list to store info
    root_url = "https://www.procyclingstats.com/rankings.php?"
    date = "2025-05-22"   # assuming this will change throughout the season so update accordingly
    opts = "&nation=&age=&zage=&page=smallerorequal&team="
    base_url = root_url + date + opts
    rotate_url(base_url)
    print(ranking)   # could also be output to a CSV or another preferred method of consumption...
