import requests
from bs4 import BeautifulSoup

data = []

for n in range(1, 4):    # adjust to the total number of pages + 1
    url = f"https://www.ctlottery.org/ajax/getWinnerListPage?p={n}"
    headers = {'Referer': 'https://www.ctlottery.org/winners', }
    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
    table = soup.find('table')  # find the <table> element on the page and focus search there

    if table:
        for row in table.find_all('tr'):
            # Find all 'td' (table data) cells within the current row
            columns = row.find_all('td')

            if len(columns) >= 5:  # Ensure there are enough columns to avoid index errors
                date = columns[0].get_text(strip=True)  # Get text content of the first td

                # Get the text content of the 'who' column
                whowhere = columns[1].get_text(separator="\n", strip=True)

                # Split the who_content by the newline character
                # BeautifulSoup often replaces <br> with a newline when using get_text(separator="\n")
                who_parts = whowhere.split('\n')

                name = ""
                place = ""

                if len(who_parts) > 0:
                    name = who_parts[0].strip()  # Get the first part (name)
                if len(who_parts) > 1:
                    place = who_parts[1].strip()  # Get the second part (place)

                retailer = columns[2].get_text(strip=True)
                game = columns[3].get_text(strip=True)
                prize = columns[4].get_text(strip=True)
                data.append([date, name, place, retailer, game, prize])

    else:
        print("Table not found")

print(data)
