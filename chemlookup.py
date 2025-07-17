import requests
import csv


file_path = "chemicals.csv"
chemicals = []

# Open a file and iterate through the lines, looking for a certain value
try:
    with open(file_path, 'r', encoding='utf8') as file:
        reader = csv.reader(file) # Use csv.reader to handle CSV formatting
        for row in reader:
            chemicals.append(row) # Add the row (as a list of strings) if it contains "instances"

except FileNotFoundError:
    print(f"Error: File not found at '{file_path}'")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

for chem in chemicals:
    cookies = {
        'cck1': '%7B%22cm%22%3Afalse%2C%22all1st%22%3Afalse%7D',
        'legalNotice': '%7B%22accepted%22%3Atrue%2C%22expired%22%3Afalse%2C%22acceptedDate%22%3A1752730373741%7D',
    }

    headers = {
        'Host': 'chem.echa.europa.eu',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:140.0) Gecko/20100101 Firefox/140.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'DNT': '1',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Referer': f'https://chem.echa.europa.eu/substance-search?searchText={chem}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    params = {
        'pageIndex': '1',
        'pageSize': '100',
        'searchText': chem,
    }

    response = requests.get('https://chem.echa.europa.eu/api-substance/v1/substance', params=params, cookies=cookies, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            # Get the first item from the returned JSON
            first_item = data["items"][0]
            if "substanceIndex" in first_item:
                name = first_item["substanceIndex"].get("rmlName", "N/A")
                code = first_item["substanceIndex"].get("rmlEc", "N/A")
                print(f"Chemical: {chem}, Name: {name}, EC Code: {code}")
            else:
                print(f"No 'substanceIndex' found in the first item for chemical: {chem}")
        else:
            print(f"No results found for chemical: {chem}")
    else:
        print(f"Failed to retrieve data for {chem}. Status code: {response.status_code}")
