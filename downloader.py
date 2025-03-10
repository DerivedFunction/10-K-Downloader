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
    with open(failOutFile, "a+") as file:
        print(f"Company not found: {out}\n")
        file.write(f'{out}\n')
def get_json(token):
    """
    A GET request to https://data.sec.gov/submissions/CIK##########.json, which will return a JSON
    response of filing data for that company. Constructs 10-K links from both recent and older filings.

    Returns:
        Array of [name, date, link, ticker]
    """
    ticker = token[0]
    cik = token[1].zfill(10)
    links = []
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": f'cik {cik}@{ticker}.com'}
    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            name = data.get("name")
            if not name:
                writeFail(cik)
                return links

            # Process recent filings
            filings = data.get("filings", {}).get("recent", {})
            filing_urls = filings.get("primaryDocument", [])
            filing_types = filings.get("form", [])
            filing_dates = filings.get("filingDate", [])
            report_dates = filings.get("reportDate", [])
            accession_numbers = filings.get("accessionNumber", [])

            for i in range(len(filing_types)):
                if filing_types[i] == "10-K":  # You can add "10-K/A" here if amendments are needed
                    accession_number = accession_numbers[i].replace("-", "")
                    link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{filing_urls[i]}"
                    date = [filing_dates[i], report_dates[i]]
                    links.append([name, date, link, ticker])

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
                        if filing_types[i] == "10-K":  # Again, add "10-K/A" if needed
                            accession_number = accession_numbers[i].replace("-", "")
                            link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{filing_urls[i]}"
                            date = [filing_dates[i], report_dates[i]]
                            links.append([name, date, link, ticker])

    except urllib.error.URLError as e:
        print(f"Failed to connect to {url}: {e.reason}\n")
        writeFail(cik)

    if not links:
        print("No 10-K links for", ticker, cik)
        writeFail(f'{ticker}\t{cik}')
    return links

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
        date = data[1][0]
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
        
    start_year = input("Enter start reporting year (e.g., 2004): ")
    end_year = input("Enter end reporting year (e.g., 2006): ")
    
    try:
        start_year = int(start_year)
        end_year = int(end_year)
        
        # Define column headers and widths
        headers = ["Report Date", "Filing Date", "Company", "Link"]
        widths = [12, 12, 30, 100]  # Adjust these widths as needed
        
        # Print header
        print(f"\nFilings between {start_year} and {end_year}:")
        print("\n" + "".join(f"{header:<{width}}" for header, width in zip(headers, widths)))
        print("-" * sum(widths))
        
        # Print data rows
        for link in links:
            report_date = link[1][1]  # Get report date
            year = int(report_date.split('-')[0])  # Extract year from date
            
            if start_year <= year <= end_year:
                name = link[0]
                filing_date = link[1][0]
                url = link[2]
                
                # Format and print row
                row = [
                    report_date[:10],  # Trim date to YYYY-MM-DD
                    filing_date[:10],  # Trim date to YYYY-MM-DD
                    name[:28] + ".." if len(name) > 30 else name,  # Truncate long names
                    url      # Truncate long URLs
                ]
                print("".join(f"{col:<{width}}" for col, width in zip(row, widths)))
                
    except ValueError:
        print("Please enter valid years in YYYY format")
    
    print("\nPress enter to clear", end="")
    input()
        


def parse_cik():
    """
    Fetches SEC's list of ticker to CIK values for approximately 12,000 companies.
    
    This function sends a GET request to the SEC's website, parses the response, and stores the ticker to CIK values in an array.
    
    Returns:
        list: An array of [ticker, cik] pairs, where 'ticker' is a company's ticker symbol and 'cik' is the corresponding CIK code.
    """
    
    # Stores each company's [ticker, cik] pair
    cik_list = []

    # Send a GET request to the SEC's website
    headers = {"User-Agent": "test test@test.com"}  # Include a user agent header
    request = urllib.request.Request('https://www.sec.gov/include/ticker.txt', headers=headers)
    with urllib.request.urlopen(request) as response:
        # Read each line for ticker and CIK. Append it to the array.
        lines = response.read().decode('utf-8').splitlines()
        print(f'Matched {len(lines)} ticker to CIK values')
        for line in lines:
            token = line.strip().split('\t')
            if len(token) > 1:
                cik_list.append([token[0], token[1].zfill(10)])
    
    # Return final array
    return cik_list



def download_multiple(companies):
    """
    Download each company based on its CIK or ticker
    """
    for i, company in enumerate(companies):
        get_cik(company)


def download_all(companies):
    """
    Directly download from the array given
    """
    download_multiple(companies)

def download_one(companies):
    """
    Directly download one value based on its CIK or ticker
    """
    cik = input("Enter the CIK or ticker of the company: ")
    token = next((company for company in companies if company[0] == cik or company[1] == cik.zfill(10)), None)
    if token:
        get_cik(token)
    else:
        get_cik([cik, cik])
        
def view_one(companies):
    """
    Directly download one value based on its CIK or ticker
    """
    cik = input("Enter the CIK or ticker of the company: ")
    token = next((company for company in companies if company[0] == cik or company[1] == cik.zfill(10)), None)
    if token:
        view_cik(token)
    else:
        view_cik([cik, cik])

def download_multiple_from_file(companies):
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
                        company = next((comp for comp in companies if comp[0] == cik or comp[1] == cik.zfill(10)), None)
                        if cik not in processed_companies:
                            if company:
                                company_list.append(company)
                            else: 
                                company_list.append([cik, cik])
                            processed_companies.append(cik)
                                
            # Call the `download_multiple` function to download the list
            download_multiple(company_list)
    # Read from terminal output
    else:
        # Parse the tokens
        print("Skipping file input, reading from terminal. Enter CIKs/tickers separated by commas:")
        tokens = input("Values: ")
        if tokens:
            ciks = tokens.replace('\t', ',').replace('\n', ',').split(',')
            for cik in ciks:
                cik = cik.strip().zfill(10)
                company = next((comp for comp in companies if comp[0] == cik or comp[1] == cik), None)
                if company and company[1] not in processed_companies:
                    company_list.append(company)
                    processed_companies.add(company[1])
                else:
                    if not company:
                        company_list.append([cik, cik])
                    processed_companies.add(cik)
            # Call the `download_multiple` function to download the list
            download_multiple(company_list)
        else:
            print("No input")
            
def main_menu():
    """
    Main menu gives a terminal-like user interface.
    """
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
    print("=== 10-K Downloader ===")
    print("1: Download filings from [A]ll companies")
    print("2: Download filings for [O]ne company by CIK/ticker")
    print("3: Download filings for [M]ultiple companies by CIKs/tickers")
    print("4: [V]iew filings for One company by CIK/ticker")
    print("0: [E]xit")
    choice = input("Choose an option: ")
    return choice

def main():
    """
    Main waits for user inputs for the command
    """
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
        elif choice in ['4', 'V', 'v']:
            view_one(companies)
        elif choice in ['0', 'E', 'e']:
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

# File output for any company with no 10-K links
failOutFile = "fail_cik.txt"
if __name__ == "__main__":   
    main()

