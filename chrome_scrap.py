from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Initialize the WebDriver (e.g., Chrome)
driver = webdriver.Chrome()

# Navigate to the website
driver.get("https://app.prizepicks.com/")  # Replace with the actual website URL

try:
    # Scroll down to trigger dynamic loading
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for 2 seconds after scrolling

    # Wait for the league-navigation elements to be present
    sports_buttons = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'league-navigation'))
    )
    print(f"Found {len(sports_buttons)} sports categories.")

    # Iterate through the elements and extract data
    for button in sports_buttons:
        # Example: Print the text of each button
        print(button.text)
        # Example: Get the href attribute if it's an anchor tag
        # if button.tag_name == 'a':
        #     print(button.get_attribute('href'))

except TimeoutException:
    print("No sports categories found.")
finally:
    driver.quit()