import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set the URL and password
DROPBOX_URL = 'your_dropbox_url_here'
DROPBOX_PASSWORD = 'your_password_here'

def download_from_dropbox():
    # Set up WebDriver options
    options = Options()
    
    # Set the download directory
    # download_dir = r"D:\your\dir" ## for windows
    download_dir ="your/path/dir"
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    # Set up the Chrome driver service
    service = ChromeService(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(DROPBOX_URL)
        
        # Wait for the page to load and find the password input field
        time.sleep(3)   
        password_input = driver.find_element(By.NAME, 'shared-link-password')  # Adjust selector as needed
        password_input.send_keys(DROPBOX_PASSWORD)
        password_input.send_keys(Keys.RETURN)

        # Wait for the file to be accessible
        time.sleep(5)

        folder_link = driver.find_element(By.XPATH, '//a[@data-testid="sl-list-column--name" and contains(@aria-label, "FOLDER")]') # if any have an folder adjust if needed
        folder_link.click()

        time.sleep(3)
        
        header_cell =  driver.find_element(By.XPATH, '//div[@role="columnheader" and @data-testid="sl-list-header--modified"]//button') # sort by new
        header_cell.click()
        time.sleep(1)
        header_cell.click()
        time.sleep(3)
        
        yesterday_date = (datetime.now() - timedelta(1)).strftime('%y%m%d') # sample for yesterday date

        file_name_pattern = f"filename_pattern_{yesterday_date}_"
        file_xpath = f'//a[contains(@aria-label, "{file_name_pattern}") and contains(@aria-label, ".zip")]' #change .zip as the extensions your real file

        file_link = driver.find_element(By.XPATH, file_xpath)
        action = ActionChains(driver)
        action.move_to_element(file_link).perform()

        time.sleep(2)
        
        # Locate the download button
        download_button = driver.find_element(By.XPATH, '//button[@data-testid="list-item-hover-download-button"]')
        download_button.click()

        # Wait for the modal to appear
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'folder-preview-modal')))

        # Locate the "Or continue with download only" button and click it
        continue_download_button = driver.find_element(By.XPATH, '//button[contains(@class, "dig-Button") and contains(@class, "dig-Button--transparent") and contains(@class, "dig-Button--standard") and contains(@class, "dig-Button--medium") and contains(@class, "dig-Button-tone--neutral")]//span[text()="Or continue with download only"]')
        continue_download_button.click()

        # Monitor the download directory for the downloaded file
        start_time = time.time()
        timeout = 300  # Set a timeout for 5 minutes

        while time.time() - start_time < timeout:
            try:
                files = os.listdir(download_dir)
                for file_name in files:
                    if file_name.startswith(file_name_pattern) and file_name.endswith(".zip"): #adjust extension 
                        print("Download completed successfully.")
                        return
            except Exception as e:
                print(f"Error while checking download directory: {e}")
            
            time.sleep(5)  # Wait for a while before checking again

        print("Download did not complete within the expected time.")
        
    finally:
        driver.quit()
        
def main():
    download_from_dropbox()

if __name__ == "__main__":
    main()
