# 10-K Downloader

#### Downloads SEC 10-K filings from various companies.

## How it works:

- Fetches a list of ticker/CIK pairs from [SEC's website](https://www.sec.gov/include/ticker.txt).
- Uses [SEC's APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) to find each entity’s current filing history.

## Features

- Download filings for **all companies** listed on the SEC's website.
- Download filings for **one specific company** by providing its CIK/ticker.
- Download filings for **multiple companies** by providing a file with CIKs/tickers or entering them manually.
- Displays a progress bar to track the download progress.

## Prerequisites

- Python 3.x installed on your system.
- Required Python packages: `urllib`, `json`, `os`, `pathlib`, and `tqdm`.

## Installation for Python Script

1. Clone the repository:
   ```sh
   git clone https://github.com/YourUsername/10-K-Downloader.git
   cd 10-K-Downloader
2. Install the required packages using `pip install`.
3. Follow the on-screen prompts to select your desired option:

  - Option 1: Download filings from all companies.
  
  - Option 2: Download filings for one company by CIK/ticker.
  
  - Option 3: Download filings for multiple companies by CIKs/tickers (via a file or terminal input).
  
  - Option 0: Exit the program.
# Optional: This may slow down the computer, or be distracting
## Using the UserScript to Highlight key financial words
1. Install TamperMonkey
2. Enable Developer Mode and allow TamperMonkey to access local files
3. Add `10K-Highlighter.js` as a new script.
4. Open a local 10-K file already downloaded in the `10K` folder

