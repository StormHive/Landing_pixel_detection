from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# from seleniumwire import webdriver
import re 
import time

def is_element_invisible(driver, element):
    # Use JavaScript to check if the element is visible
    return driver.execute_script(
        "var style = window.getComputedStyle(arguments[0]);"
        "return style || style.display === 'none' || style.opacity === '0' || style.visibility === 'hidden';",
        element
    )

def find_landing_pixels(url):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without opening GUI)

    # Set the path to the ChromeDriver executable
    driver = webdriver.Chrome()
    # Initialize the Chrome driver

    try:
        # Navigate to the specified URL
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        driver.get(url)

        # Wait for the page to load completely
        time.sleep(5)  # Adjust the sleep time as needed

        html_source = driver.page_source

        # Find all script tags on the page
        script_tags = driver.find_elements(By.TAG_NAME, 'script')

        # Find all image tags on the page
        img_tags = driver.find_elements(By.TAG_NAME, 'img')

        # Find all iframe tags on the page
        iframe_tags = driver.find_elements(By.TAG_NAME, 'iframe')

        # Initialize a list to store landing pixels
        landing_pixels = []

        requests = driver.execute_script("""
            return performance.getEntriesByType('resource').map(function(entry) {
                return {
                    url: entry.name,
                    type: entry.initiatorType
                };
            });
        """)
        # Define known tracking services
        tracking_services = {
            "ip-api.com": "Location and IP tracking",  # Provides information about the user's IP address and location
            "ipinfo.io": "Location and IP tracking",  # Offers details about the user's IP address and location
            "whatismybrowser.com": "Browser information tracking",  # Collects information about the user's browser
            "maxmind.com": "Location and IP tracking",  # Provides geolocation data based on the user's IP address
            "browserleaks.com": "Browser information tracking",  # Collects various browser-related information
            "bugsnag.com": "Error tracking and logging",  # Used for error monitoring and tracking on websites
            "hotjar.com": "User behavior tracking",  # Tracks user interactions and behavior on websites
            "google-analytics.com": "Website analytics tracking",  # Google Analytics service for tracking website traffic
            "facebook.com/tr": "Facebook Pixel tracking",  # Facebook Pixel for tracking user interactions on websites
            "mouseflow.com": "Mouseflow tracking",  # Tracks user behavior and interactions on websites
            "crazyegg.com": "Crazy Egg tracking",  # Tracks user behavior and interactions on websites
            "qualtrics.com": "Qualtrics tracking",  # Tracks user behavior and interactions on websites
            "mixpanel.com": "Mixpanel tracking",  # Tracks user behavior and interactions on websites
            "segment.com": "Segment tracking",  # Collects and sends data to various analytics and marketing tools
            "optimizely.com": "Optimizely tracking",  # A/B testing and experimentation platform that tracks user interactions
            "vwo.com": "VWO tracking",  # A/B testing and conversion optimization platform that tracks user interactions
            "salesforce.com": "Salesforce Marketing Cloud tracking",  # Tracks customer interactions and engagement for marketing purposes
            "hubspot.com": "HubSpot tracking",  # Tracks user interactions and engagement for marketing and sales purposes
            "whatismybrowser.com": "Browser information tracking",  # Collects information about the user's browser
            "clicktale.com": "User experience analytics",  # Analyzes user interactions to improve website usability
            "tealium.com": "Tag management and customer data platform",  # Manages tags and integrates customer data
            "krux.com": "Data management platform",  # Collects and analyzes audience data for marketing purposes
            "adobe.com/analytics": "Adobe Analytics",  # Adobe's analytics platform for tracking website performance
            "clarity.ms": "User behavior tracking",
        }
        for request in requests:
            for service_url, service_description in tracking_services.items():
                if service_url in request['url']:
                    landing_pixels.append({service_url:service_description})

        # Iterate over script tags and check for Google Analytics or Facebook Pixel
        for script in script_tags:
            try:
                src = script.get_attribute('src')
                script_text = script.get_attribute('innerHTML')
            except StaleElementReferenceException:
                continue
            if src:
                if 'google-analytics' in src or 'facebook.com/tr' in src or 'facebook.net' in src or 'reportWebVitals' in src:
                    landing_pixels.append(src)
            #src_match = re.search(r'(\S*)\.src\s*=\s*[\'"]([^\'" >]+\.gif)', script_text)
            if 'https://connect.facebook.net/en_US/fbevents.js' in script_text or 'new Image()' in script_text:
                landing_pixels.append(script_text)            
       
        #In Facebookpixel in HTML 
        if 'https://connect.facebook.net/en_US/fbevents.js' in html_source or 'reportWebVitals()' in html_source:
            landing_pixels.append(html_source)

        # Iterate over img tags and check for Google Analytics or Facebook Pixel
        for img in img_tags:
            try:
                src = img.get_attribute('src')
            except StaleElementReferenceException:
                continue
            if src:
                if 'google-analytics' in src or 'facebook.com/tr' in src:
                    landing_pixels.append(src)
                width = img.get_attribute('width')
                height = img.get_attribute('height')
                # Check if the image has dimensions 1x1 or 0x0, ends with '.gif', and is visible
                if width in ['1', '0'] or height in ['1', '0'] or is_element_invisible(driver, img) and src.endswith('.gif'):
                    landing_pixels.append(src)

        # Iterate over iframe tags and check for Google Analytics or Facebook Pixel
        for iframe in iframe_tags:
            src = iframe.get_attribute('src')
            if src:
                if 'google-analytics' in src or 'facebook.com/tr' in src:
                    landing_pixels.append(src)

        # Print the found landing pixels
        if landing_pixels:
            print("Landing pixels found:")
            for pixel in landing_pixels:
                print(pixel)
        else:
            print("No landing pixels found.")

    except Exception as e:
        print("An error occurred:", e)

    finally:
        # Close the browser
        driver.quit()

# Example usage:
website_url = 'https://www.opera.com/'
find_landing_pixels(website_url)