# Check and install missing packages
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import urllib.request
except ImportError:
    install('urllib')

try:
    import json
except ImportError:
    install('json')

try:
    import os
except ImportError:
    install('os')

try:
    from pathlib import Path
except ImportError:
    install('pathlib')

try:
    from tqdm import tqdm
except ImportError:
    install('tqdm')


import urllib.request
import json
import os # Create folders
from pathlib import Path # Find if file exists
from tqdm import tqdm # Progress bar

def get_json(token):
    ticker = token[0]
    cik = token[1]
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": f'cik {cik}@{ticker}.com'}  # Include a user agent header
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode())

        links = []
        name = data.get("name")
        if not name:
            print("Name not found for CIK:", cik)
            return links

        filings = data.get("filings", {}).get("recent", {})
        filing_urls = filings.get("primaryDocument", [])
        filing_types = filings.get("form", [])
        filing_dates = filings.get("filingDate", [])

        url_size = len(filing_urls)
        date_size = len(filing_dates)
        
        for i, type in enumerate(filing_types):
            if type == "10-K" and i < url_size and i < date_size:
                # Create the link to the 10-K filing
                accession_number = filings.get("accessionNumber", [])[i].replace("-", "")
                if accession_number:
                    cik_pad = cik.zfill(10)  # Ensure CIK is 10 digits with leading zeros
                    link = f"https://www.sec.gov/Archives/edgar/data/{cik_pad}/{accession_number}/{filing_urls[i]}"
                    date = filing_dates[i]
                    # Add the link to the list
                    links.append([name, date, link, ticker])
    if not links:
        print("No 10-K links for", ticker, cik)
    return links

def open_links(links):
    if not links:
        print("No links to open.")
        return

    ticker = links[0][3]
    name = links[0][0]
    # Check if directory exists
    if not os.path.exists(f'./10K/{ticker}'):
        # Create directory
        os.makedirs(f'./10K/{ticker}')
    
    # Initialize tqdm progress bar
    progress_bar = tqdm(total=len(links), desc=f"\nDownloading 10-K filings for {name} - {ticker}")

    for idx, data in enumerate(links):
        name = data[0].replace("/", " ")
        date = data[1]
        url = data[2]
        filename = f"./10K/{ticker}/{date}.html"
        if Path(filename).exists():
            progress_bar.update(1)
            continue
        headers = {"User-Agent": f'{name} {date}@{ticker}.com'}  # Include a user agent header
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            html_content = response.read().decode()
            with open(filename, "w") as file:
                file.write(html_content)
                # Update progress bar
                progress_bar.update(1)

    # Close the progress bar
    progress_bar.close()
            

def get_cik(token):
    links = get_json(token)
    open_links(links)

def parse_cik():
    cik_list = []
    headers = {"User-Agent": f'test test@test.com'}  # Include a user agent header
    request = urllib.request.Request('https://www.sec.gov/include/ticker.txt', headers=headers)
    with urllib.request.urlopen(request) as response:
        # error here (response is plain text file
        lines = response.read().decode('utf-8').splitlines()
        print(f'Found {len(lines)} CIK values')
        for line in lines:
            token = line.strip().split('\t')
            if len(token) > 1:
                cik_list.append([token[0], token[1].zfill(10)])
    return cik_list

def download_multiple(companies):
    for i, company in enumerate(companies):
        get_cik(company)

def download_all(companies):
    download_multiple(companies)

def download_one(companies):
    cik = input("Enter the CIK or ticker of the company: ")
    token = next((company for company in companies if company[0] == cik or company[1] == cik.zfill(10)), None)
    if token:
        get_cik(token)
    else:
        print("Company not found.")

def download_multiple_from_file(companies):
    print("Each ticker/CIK must be separated by commas")
    company_list = []
    filename = input("Enter filename to read (or press enter to read from terminal): ")
    if filename:
        if not Path(filename).exists():
            print(f"File not found.")
        else:
            with open(filename, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    token = line.strip().split('\t')
                    if len(token) > 1:
                        cik = token[1].zfill(10)
                        company = next((comp for comp in companies if comp[0] == token[0] or comp[1] == cik), None)
                        if company:
                            company_list.append(company)
                        else:
                            print(f"Company not found: {token[0]}")
            download_multiple(company_list)
    else:
        print("Skipping file input, reading from terminal. Enter CIKs/tickers separated by commas:")
        tokens = input("Values: ")
        if tokens:
            ciks = tokens.split(',')
            for cik in ciks:
                cik = cik.strip()
                company = next((comp for comp in companies if comp[0] == cik or comp[1] == cik.zfill(10)), None)
                if company:
                    company_list.append(company)
                else:
                    print(f"Company not found: {cik}")
            download_multiple(company_list)
        else:
            print("No input")
            
def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
    print("=== 10-K Downloader ===")
    print("1: Download filings from [A]ll companies")
    print("2: Download filings for [O]ne company by CIK/ticker")
    print("3: Download filings for [M]ultiple companies by CIKs/tickers")
    print("0: [E]xit")
    choice = input("Choose an option: ")
    return choice

def main():
    if not os.path.exists('./10K'):
        # Create directory
        os.makedirs('./10K')
    companies = parse_cik()
    while True:
        choice = main_menu()
        if choice in ['1', 'A', 'a']:
            download_all(companies)
        elif choice in ['2', 'O', 'o']:
            download_one(companies)
        elif choice in ['3', 'M', 'm']:
            download_multiple_from_file(companies)
        elif choice in ['0', 'E', 'e']:
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":   
    main()

