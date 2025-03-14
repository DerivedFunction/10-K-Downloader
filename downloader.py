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

def writeFail(out):
    with open(FAIL_FILE, "a+") as file:
        print(f"Company not found: {out}\n")
        file.write(f'{out}\n')

def get_json(token):
    """
    A GET request to https://data.sec.gov/submissions/CIK##########.json, which will return a JSON
    response of filing data for that company. Constructs 10-K links from both recent and older filings.

    Returns:
        Array of [name, date, link, ticker]
    """
    cik = token.zfill(10)
    links = []
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    print(f"Searching: {url}\n")
    headers = {"User-Agent": f'cik {cik}@{cik}.com'}
    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            name = data.get("name")
            if not name:
                writeFail(cik)
                return links
            ticker = data.get("tickers",[])[0] if len(data.get("tickers",[])) > 0 else cik
            # Process recent filings
            filings = data.get("filings", {}).get("recent", {})
            filing_urls = filings.get("primaryDocument", [])
            filing_types = filings.get("form", [])
            filing_dates = filings.get("filingDate", [])
            report_dates = filings.get("reportDate", [])
            accession_numbers = filings.get("accessionNumber", [])
            
            for i in range(len(filing_types)):
                if filing_types[i] in FILING_TYPES:  # You can add "10-K/A" here if amendments are needed
                    accession_number = accession_numbers[i].replace("-", "")
                    link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{filing_urls[i]}"
                    date = [filing_dates[i], report_dates[i]]
                    links.append([name, date, link, ticker, filing_types[i]])
            
            # Process older filings if they exist
            older_filings = data.get("filings", {}).get("files", [])
            
            for filing in older_filings:
                filing_url = f"https://data.sec.gov/submissions/{filing['name']}"
                filing_request = urllib.request.Request(filing_url, headers=headers)
                with urllib.request.urlopen(filing_request) as filing_response:
                    filing_data = json.loads(filing_response.read().decode())
                    filing_urls = filing_data.get("primaryDocument", [])
                    filing_types = filing_data.get("form", [])
                    filing_dates = filing_data.get("filingDate", [])
                    report_dates = filing_data.get("reportDate", [])
                    accession_numbers = filing_data.get("accessionNumber", [])

                    for i in range(len(filing_types)):
                        if filing_types[i] in FILING_TYPES: 
                            accession_number = accession_numbers[i].replace("-", "")
                            link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{filing_urls[i]}"
                            date = [filing_dates[i], report_dates[i]]
                            links.append([name, date, link, ticker, filing_types[i]])
        if not links:
            print("No 10-K links for", ticker, cik)
            writeFail(f'{ticker}\t{cik}')
        return links

    except urllib.error.URLError as e:
        print(f"Failed to connect to {url}: {e.reason}\n")
        writeFail(cik)

def open_links(links):
    """
    Attempts to connect to each link in the links array. It will write the response into a file,
    effectively downloading it. Each html file is the 10-K report
    """
    # Empty array
    if not links:
        return
    ticker = links[0][3]
    name = links[0][0]
    # Check if directory exists
    if not os.path.exists(f'./10K/{ticker}'):
        # Create directory
        os.makedirs(f'./10K/{ticker}')
    
    # Initialize tqdm progress bar
    progress_bar = tqdm(total=len(links), desc=f"\nDownloading 10-K filings for {name} - {ticker}")
    
    # Open and download each link 
    for data in links:
        name = data[0].replace("/", " ")
        date = data[1][1]
        url = data[2]
        filename = f"./10K/{ticker}/{date}.html"
        if Path(filename).exists():
            progress_bar.update(1)
            continue
        headers = {"User-Agent": f'{name} {date}@{ticker}.com'}  # Include a user agent header
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request) as response:
                html_content = response.read().decode()
                with open(filename, "w") as file:
                    file.write(html_content)
        except urllib.error.URLError as e:
            print(f"Failed to connect to {url}: {e.reason}\n")
        os.system('cls' if os.name == 'nt' else 'clear')
        progress_bar.update(1)

    # Close the progress bar
    progress_bar.close()
            

def get_cik(token):
    """
    Gets SEC's JSON response for a specific company first to find all of its recent filings.
    Then, it will attempt to download the files via `open_links`
    """
    links = get_json(token)

    open_links(links)
    
def view_cik(token):
    """
    Gets SEC's JSON response for a specific company first to find all of its recent filings.
    Then, it will attempt to view the links via `view_links`
    """
    links = get_json(token)

    view_links(links)
    
def view_links(links):
    """
    Display 10-K filings within a specified year range in a table format.
    Links are sorted in descending order by date.
    """
    if not links:
        return
    start_year = input("Enter start reporting year: ").strip()
    end_year = input("Enter end reporting year: ").strip()
    name = links[0][0]
    try:
        start_year = int(start_year)
        end_year = int(end_year)
        
        # Define column headers and widths
        headers = ["Type", "Filing Date", "Report Date", "Link"]
        widths = [8, 12, 12, 100]
        
        # Print header
        print(f"\nFilings for {name}:")
        print("\n" + "".join(f"{header:<{width}}" for header, width in zip(headers, widths)))
        print("-" * sum(widths))
        
        # Print data rows
        for link in links:
            report_date = link[1][1]  # Get report date
            year = int(report_date.split('-')[0])  # Extract year from date
            if start_year <= year <= end_year:
                
                filing_date = link[1][0]
                url = link[2]
                type = link[4]
                # Format and print row
                row = [
                    type,
                    filing_date[:10],  # Trim date to YYYY-MM-DD
                    report_date[:10],  # Trim date to YYYY-MM-DD
                    url
                ]
                print("".join(f"{col:<{width}}" for col, width in zip(row, widths)))
                
    except ValueError:
        print("Please enter valid years in YYYY format")
        view_links(links)
        


def download_multiple(companies):
    """
    Download each company based on its CIK or ticker
    """
    for i, company in enumerate(companies):
        get_cik(company)


def download_one():
    """
    Directly download one value based on its CIK or ticker
    """
    cik = input("Enter the CIK or ticker of the company: ")
    get_cik(cik)
        
def view_one():
    """
    Directly download one value based on its CIK or ticker
    """
    cik = input("Enter the CIK or ticker of the company: ").strip()
    view_cik(cik)

def download_multiple_from_file():
    """
    Directly download one value based on its CIK or ticker from a file output
    """
    # Stores each company's [ticker, cik] pair
    company_list = []
    processed_companies = []
    # Read from file
    filename = input("Enter filename to read (or press enter to read from terminal): ")
    if filename:
        if not Path(filename).exists():
            print(f"File not found.")
        else:
            with open(filename, 'r') as file:
                # Parse the value from each line
                lines = file.readlines()
                for line in lines:
                    ciks = line.replace('\t', ',').split(',')
                    for cik in ciks:
                        cik = cik.strip()
                        if cik not in processed_companies:
                            company_list.append(cik)
                            processed_companies.append(cik)                                
            # Call the `download_multiple` function to download the list
            download_multiple(company_list)
    # Read from terminal output
    else:
        # Parse the tokens
        print("Skipping file input, reading from terminal. Enter CIKs separated by commas:")
        tokens = input("Values: ")
        if tokens:
            ciks = tokens.replace('\t', ',').replace('\n', ',').split(',')
            for cik in ciks:
                cik = cik.strip().zfill(10)
                if cik not in processed_companies:
                    company_list.append(cik)
                    processed_companies.add(cik)
            # Call the `download_multiple` function to download the list
            download_multiple(company_list)
        else:
            print("No input")
            
def main_menu():
    """
    Main menu gives a terminal-like user interface.
    """
    print("=== 10-K Downloader ===")
    print("1: Download filings for [O]ne company by CIK")
    print("2: Download filings for [M]ultiple companies by CIKs")
    print("3: [V]iew filings for One company by CIK")
    print("0: [E]xit")
    choice = input("Choose an option: ").strip()
    return choice

def main():
    """
    Main waits for user inputs for the command
    """
    if not os.path.exists('./10K'):
        # Create directory
        os.makedirs('./10K')
    while True:
        choice = main_menu()
        if choice in ['1', 'O', 'o']:
            download_one()
        elif choice in ['2', 'M', 'm']:
            download_multiple_from_file()
        elif choice in ['3', 'V', 'v']:
            view_one()
        elif choice in ['0', 'E', 'e']:
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

# File output for any company with no 10-K links
FILING_TYPES = ["10-K", "10-K/A", "20-F"]
FAIL_FILE = "fail_cik.txt"
if __name__ == "__main__":   
    main()

