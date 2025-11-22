from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from config.settings import Settings

class SeleniumHelper:
    @staticmethod
    def get_final_url_selenium(url):
        """Get final URL after redirects using Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(Settings.SELENIUM_TIMEOUT)
            
            print(f"   Opening with Selenium: {url[:80]}...")
            driver.get(url)
            
            # Wait for potential redirects
            time.sleep(3)
            
            final_url = driver.current_url
            print(f"   ✅ Final URL obtained: {final_url[:80]}...")
            return final_url
            
        except Exception as e:
            print(f"   ❌ Selenium error: {str(e)[:100]}...")
            return url
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass