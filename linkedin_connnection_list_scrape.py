import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
LINKEDIN_EMAIL = os.environ.get('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = os.environ.get('LINKEDIN_PASSWORD')
CHROMEDRIVER_PATH = "chromedriver.exe"

if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    raise ValueError("Please set the LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables in your .env file.")

# --- SELENIUM SETUP ---
options = Options()
options.add_argument('--start-maximized')
# options.add_argument('--headless')  # Uncomment to run headless
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)


def linkedin_login(email, password):
    driver.get('https://www.linkedin.com/login')
    time.sleep(2)
    driver.find_element(By.ID, 'username').send_keys(email)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(3)

def scrape_connections():
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(5)
    # --- Get total connections ---
    try:
        header = driver.find_element(By.CSS_SELECTOR, '[componentkey="ConnectionsPage_ConnectionsListHeader"]')
        total_connections = int(re.search(r'\d+', header.text.replace(',', '')).group())
        print(f"Total connections: {total_connections}")
    except Exception as e:
        print("Could not find the connections header:", e)
        driver.save_screenshot('connections_header_error.png')
        return []

    # --- Scroll until all are loaded ---
    loaded = 0
    scroll_attempts = 0
    max_attempts = 10

    while loaded < total_connections and scroll_attempts < max_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)  # Increased wait time for slow loading
        containers = driver.find_elements(By.CSS_SELECTOR, '[data-view-name="connections-list"]')
        all_cards = []
        for container in containers:
            cards = container.find_elements(By.CSS_SELECTOR, 'div[componentkey^="auto-component"]')
            all_cards.extend(cards)
        new_loaded = len(all_cards)
        print(f"Loaded {new_loaded} of {total_connections}")
        if new_loaded == loaded:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
        loaded = new_loaded

    data = []
    try:
        # Find all containers holding connections
        containers = driver.find_elements(By.CSS_SELECTOR, '[data-view-name="connections-list"]')
        all_cards = []
        for container in containers:
            cards = container.find_elements(By.CSS_SELECTOR, 'div[componentkey^="auto-component"]')
            all_cards.extend(cards)
        print(f"Found {len(all_cards)} connection cards")
        for card in all_cards:
            try:
                a_tags = card.find_elements(By.CSS_SELECTOR, 'a[data-view-name="connections-profile"]')
                profile_img = ''
                profile_url = ''
                full_name = ''
                headline = ''
                connected_on = ''
                if len(a_tags) >= 2:
                    # Profile image from first <a>
                    try:
                        profile_img = a_tags[0].find_element(By.TAG_NAME, 'img').get_attribute('src')
                    except:
                        profile_img = ''
                    # Profile URL from second <a>
                    profile_url = a_tags[1].get_attribute('href')
                    # Full name and headline from <p> tags inside second <a>
                    p_tags = a_tags[1].find_elements(By.TAG_NAME, 'p')
                    if len(p_tags) >= 1:
                        try:
                            full_name = p_tags[0].find_element(By.TAG_NAME, 'a').text.strip()
                        except:
                            full_name = p_tags[0].text.strip()
                    if len(p_tags) >= 2:
                        headline = p_tags[1].text.strip()
                    # Connected on: find the next <p> sibling after a_tags[1]
                    try:
                        parent_div = a_tags[1].find_element(By.XPATH, './../..')
                        all_p = parent_div.find_elements(By.TAG_NAME, 'p')
                        for p in all_p:
                            if 'Connected on' in p.text:
                                connected_on = p.text.strip()
                                # Format to yyyy-mm-dd
                                match = re.search(r'Connected on (.+)', connected_on)
                                if match:
                                    date_str = match.group(1).strip()
                                    try:
                                        date_obj = datetime.strptime(date_str, '%B %d, %Y')
                                        connected_on = date_obj.strftime('%Y-%m-%d')
                                    except Exception:
                                        pass
                                break
                    except:
                        connected_on = ''
                data.append({
                    'Profile URL': profile_url,
                    'Full Name': full_name,
                    'Headline': headline,
                    'Profile Image': profile_img,
                    'Connected On': connected_on
                })
            except Exception as e:
                print("Error extracting a card:", e)
    except Exception as e:
        print("Could not find the main connections list:", e)
        driver.save_screenshot('connections_page_error.png')
    return data


def main():
    linkedin_login(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
    connections = scrape_connections()
    df = pd.DataFrame(connections)
    df.to_csv('linkedin_connections.csv', index=False)
    print(f"Exported {len(df)} connections to linkedin_connections.csv")
    driver.quit()

if __name__ == '__main__':
    main()
