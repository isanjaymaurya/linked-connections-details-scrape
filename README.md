# LinkedIn Connections Details Scraper

This project scrapes your LinkedIn connections' details such as name, company name, designation, and contact details using Python.

## Features
- Scrape connection names
- Scrape company names
- Scrape designations
- Scrape contact details
- Export data to CSV

## Setup

1. **Clone the repository**
2. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Mac/Linux
   ```
3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
4. **Configure your LinkedIn credentials:**
   - Copy `env.sample` to `.env` and fill in your LinkedIn email and password:
     ```
     cp env.sample .env  # On Linux/Mac
     # or manually create .env on Windows
     ```
   - Edit `.env`:
     ```
     LINKEDIN_EMAIL=your_email@example.com
     LINKEDIN_PASSWORD=your_password
     ```
   - Your credentials will be loaded automatically using [python-dotenv](https://pypi.org/project/python-dotenv/).

## Usage

- Run the main script after configuring your LinkedIn credentials and driver path.
- The script will export the scraped data to a CSV file.

## Note
- Scraping LinkedIn may violate their terms of service. Use this tool responsibly and only for personal data export.
- You will need to download the appropriate [ChromeDriver](https://sites.google.com/chromium.org/driver/) or [GeckoDriver](https://github.com/mozilla/geckodriver/releases) for Selenium and place it in your project directory or set its path in the script.
- **Never commit your real `.env` file to version control. Use `env.sample` as a template.** 