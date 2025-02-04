from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import random


# Set up ChromeDriver in headless mode
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
driver_path = '/usr/local/bin/chromedriver'  # Replace with your path
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Access PrizePicks website
url = 'https://app.prizepicks.com/'
driver.get(url)
time.sleep(3)

try:
    # Wait for the pop-up close button to appear (adjust the class name as needed)
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'popup-close'))
    )
    close_button.click()  # Close the pop-up
    print("Pop-up closed.")
except (NoSuchElementException, TimeoutException):
    print("No pop-up found. Continuing...")

# Collect props data
props = []

# Find sports categories
try:
    sports_buttons = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'league-navigation'))
    )
    print(f"Found {len(sports_buttons)} sports categories.")
except TimeoutException:
    print("No sports categories found.")
    driver.quit()
    exit()

# Loop through each sport category
for sport_button in sports_buttons:
    try:
        sport_button.click()
        time.sleep(random.uniform(1, 3))  # Random delay to avoid detection

        # Extract player props
        players = driver.find_elements(By.CLASS_NAME, 'player-class')
        for player in players:
            try:
                player_name = player.find_element(By.CLASS_NAME, 'player-name-class').text
                prop_type = player.find_element(By.CLASS_NAME, 'prop-type-class').text
                prop_value = player.find_element(By.CLASS_NAME, 'prop-value-class').text

                if player_name and prop_type and prop_value:
                    props.append({'Player': player_name, 'Prop Type': prop_type, 'Prop Value': prop_value})
            except NoSuchElementException:
                continue  # Skip if any element is missing
    except Exception as e:
        print(f"Error processing sport category: {e}")

# Convert to DataFrame and export to CSV
if props:
    df = pd.DataFrame(props)
    csv_file_path = '/path/to/your/directory/prizepicks_props.csv'
    df.to_csv(csv_file_path, index=False)
    print(f"Data saved to {csv_file_path}")
else:
    print("No data collected.")

# Close browser
driver.quit()