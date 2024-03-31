import re 
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

class TrackLandingPixe():
    def __init__(self, url) -> None:
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome()
        self.landing_pixels = []
        self.url = url
        self.csv_file = "Output.csv"
        self.tracking_services = {
            "ip-api.com": "Location and IP tracking",  
            "ipinfo.io": "Location and IP tracking", 
            "whatismybrowser.com": "Browser information tracking", 
            "maxmind.com": "Location and IP tracking",  
            "browserleaks.com": "Browser information tracking", 
            "bugsnag.com": "Error tracking and logging",
            "hotjar.com": "User behavior tracking", 
            "google-analytics.com": "Website analytics tracking", 
            "facebook.com/tr": "Facebook Pixel tracking",  
            "mouseflow.com": "Mouseflow tracking", 
            "crazyegg.com": "Crazy Egg tracking",  
            "qualtrics.com": "Qualtrics tracking",  
            "mixpanel.com": "Mixpanel tracking",  
            "segment.com": "Segment tracking",  
            "optimizely.com": "Optimizely tracking",  
            "vwo.com": "VWO tracking",  
            "salesforce.com": "Salesforce Marketing Cloud tracking", 
            "hubspot.com": "HubSpot tracking", 
            "whatismybrowser.com": "Browser information tracking",  
            "clicktale.com": "User experience analytics",  
            "tealium.com": "Tag management and customer data platform", 
            "krux.com": "Data management platform",  
            "adobe.com/analytics": "Adobe Analytics",  
            "clarity.ms": "User behavior tracking",
        }
        self.landing_pixel_domain = ["google-analytics", "facebook.com/tr", "facebook.net", "reportWebVitals", 'acebook.com/tr']
        self.landing_pixel_urls = ['https://connect.facebook.net/en_US/fbevents.js', 'reportWebVitals()', 'new Image()']


    def is_element_invisible(self,driver, element):
        return driver.execute_script(
            "var style = window.getComputedStyle(arguments[0]);"
            "return style || style.display === 'none' || style.opacity === '0' || style.visibility === 'hidden';",
            element
        )
    

    def add_data_into_csv(self, landing_pixel):
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            for pixel in landing_pixel:
                writer.writerow([pixel])


    def extract_image_tags(self, image_tags):
        for img in image_tags:
            try:
                src = img.get_attribute('src')
            except StaleElementReferenceException:
                continue
            if src:
                for domain in self.landing_pixel_domain:
                    if domain in src:
                        self.landing_pixels.append(src)
                width = img.get_attribute('width')
                height = img.get_attribute('height')
                if (width in ['1', '0'] or height in ['1', '0'] or self.is_element_invisible(self.driver, img)) and src.endswith('.gif'):
                    self.landing_pixels.append(src)
    

    def extract_script_tags(self, script_tags):
        for script in script_tags:
            try:
                src = script.get_attribute('src')
                script_text = script.get_attribute('innerHTML')
            except StaleElementReferenceException:
                print("src Not found")
                continue
            if src:
                for domain in self.landing_pixel_domain:
                    if domain in src:
                        self.landing_pixels.append(src)
            for url in self.landing_pixel_urls:
                if url in script_text:
                    self.landing_pixels.append(script_text)     


    def extract_requests(self):
        requests = self.driver.execute_script("""
                return performance.getEntriesByType('resource').map(function(entry) {
                    return {
                        url: entry.name,
                        type: entry.initiatorType
                    };
                });
            """)
        for request in requests:
            for service_url, service_description in self.tracking_services.items():
                if service_url in request['url']:
                    self.landing_pixels.append({service_url:service_description})       
    

    def extract_iframes(self, iframe_tages):
        for iframe in iframe_tages:
            try:
                src = iframe.get_attribute('src')
            except StaleElementReferenceException:
                continue
            if src:
                if 'google-analytics' in src or 'facebook.com/tr' in src:
                    self.landing_pixels.append(src)



    def find_landing_pixels(self):
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            html_source = self.driver.page_source
            script_tags = self.driver.find_elements(By.TAG_NAME, 'script')
            img_tags = self.driver.find_elements(By.TAG_NAME, 'img')
            iframe_tags = self.driver.find_elements(By.TAG_NAME, 'iframe')
            self.extract_iframes(iframe_tags)
            self.extract_requests()
            self.extract_script_tags(script_tags=script_tags)
            self.extract_image_tags(image_tags=img_tags)
            for url in self.landing_pixel_urls:
                if url in html_source:
                    self.landing_pixels.append(html_source)

            if len(self.landing_pixels) > 0:
                print(f"Landing Pixels Found! saved in {self.csv_file}")
                self.add_data_into_csv(self.landing_pixels)
            else:
                print("No Data Found!")
        except Exception as e:
            print("An error occurred:", e)

        finally:
            self.driver.quit()


if __name__ == "__main__":
    website_url = "https://www.opera.com/"
    landing_pixel_obj = TrackLandingPixe(website_url)
    landing_pixel_obj.find_landing_pixels()