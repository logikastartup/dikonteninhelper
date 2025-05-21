import configparser
import os
import time
import urllib.request
import zipfile
import re
import shutil
import platform
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from loguru import logger
from selenium.common.exceptions import TimeoutException, WebDriverException


class SeleniumCrawler:
    def __init__(self):
        # Read configuration
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        # Get settings from config
        self.browser_timeout = self.config.getint(
            "crawler", "browser_timeout", fallback=60
        )
        self.sleep_time = self.config.getint("crawler", "sleep_time", fallback=3)
        
        # Get browser path from config if specified
        self.chrome_path = self.config.get("crawler", "browser_path", fallback=None)

        # Initialize logger
        self._setup_logger()

        # Initialize browser
        self.browser = None

    def _setup_logger(self):
        """Setup logger with daily rotation"""
        log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        logger.remove()  # Remove default handler
        logger.add(
            f"logs/{time.strftime('%Y-%m-%d')}.log",
            rotation="00:00",
            format=log_format,
            level="INFO",
        )
        logger.add(lambda msg: print(msg), format=log_format, level="INFO")

    def _initialize_browser(self):
        """Initialize browser with optimized settings and better error handling"""
        try:
            logger.info("Initializing browser...")

            # Create required directories
            os.makedirs("logs", exist_ok=True)
            os.makedirs("chrome_driver", exist_ok=True)

            # Set Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=800,600")
            chrome_options.add_argument("--start-minimized")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            
            try:
                # First check if user specified browser path in config
                chrome_path = None
                
                if self.chrome_path and os.path.exists(self.chrome_path):
                    chrome_path = self.chrome_path
                    logger.info(f"Using user-configured Chrome browser at: {chrome_path}")
                else:
                    # Look for Chrome in common locations
                    possible_paths = [
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(os.path.expandvars(path)):
                            chrome_path = os.path.expandvars(path)
                            break
                
                if chrome_path:
                    logger.info(f"Chrome found at: {chrome_path}")
                    chrome_options.binary_location = chrome_path
                else:
                    logger.warning("Chrome not found! Please set browser_path in config.ini.")
                    # Try to proceed with default binary location
            except Exception as ce:
                logger.warning(f"Could not verify Chrome installation: {str(ce)}")
            
            # Check for local chromedriver in chrome_driver folder
            base_dir = os.path.dirname(os.path.abspath(__file__))
            driver_dir = os.path.join(base_dir, "chrome_driver")
            driver_path = os.path.join(driver_dir, "chromedriver.exe")
            
            # Create chrome_driver directory if it doesn't exist
            os.makedirs(driver_dir, exist_ok=True)
            
            # Check if chromedriver exists in the chrome_driver folder
            if os.path.exists(driver_path):
                logger.info(f"Using ChromeDriver from: {driver_path}")
                service = Service(executable_path=driver_path)
            else:
                # Check alternate locations
                alternate_paths = [
                    os.path.join(base_dir, "chromedriver.exe"),
                    os.path.join(base_dir, "drivers", "chromedriver.exe")
                ]
                
                driver_found = False
                for alt_path in alternate_paths:
                    if os.path.exists(alt_path):
                        logger.info(f"Using ChromeDriver from: {alt_path}")
                        service = Service(executable_path=alt_path)
                        driver_found = True
                        break
                        
                if not driver_found:
                    # Try using webdriver_manager as a last resort
                    try:
                        logger.info("Trying to use webdriver_manager...")
                        from webdriver_manager.chrome import ChromeDriverManager
                        driver_path = ChromeDriverManager().install()
                        logger.info(f"ChromeDriver installed at: {driver_path}")
                        service = Service(executable_path=driver_path)
                        driver_found = True
                    except Exception as e:
                        logger.warning(f"webdriver_manager failed: {str(e)}")
                        
                if not driver_found:
                    error_msg = (
                        "ChromeDriver not found. Please download the correct ChromeDriver version for your Chrome from\n"
                        "https://chromedriver.chromium.org/downloads\n"
                        f"and place chromedriver.exe in the {driver_dir} folder."
                    )
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            # Initialize Chrome driver with configured service
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            self.browser.set_page_load_timeout(self.browser_timeout)

            logger.info("Browser initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Error initializing browser: {str(e)}")
            logger.error("Please ensure Chrome browser is installed and up to date")
            return False

    def _get_chrome_version(self, chrome_path):
        """Get Chrome version from binary path"""
        if not chrome_path or not os.path.exists(chrome_path):
            return None
            
        try:
            # Windows version detection
            if platform.system() == "Windows":
                import winreg
                try:
                    # Try registry first (more reliable)
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Chrome\BLBeacon") as key:
                        version = winreg.QueryValueEx(key, "version")[0]
                        return version
                except Exception:
                    # Fall back to file version info
                    try:
                        output = subprocess.check_output(f'"{chrome_path}" --version', shell=True)
                        match = re.search(r'Chrome\s+([\d\.]+)', output.decode('utf-8'))
                        if match:
                            return match.group(1)
                    except Exception:
                        pass
                        
            # macOS and Linux version detection
            else:
                try:
                    output = subprocess.check_output([chrome_path, '--version'])
                    match = re.search(r'Chrome\s+([\d\.]+)', output.decode('utf-8'))
                    if match:
                        return match.group(1)
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Error detecting Chrome version: {str(e)}")
            
        return None
        
    def _download_chromedriver(self, driver_dir):
        """Download appropriate ChromeDriver version"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(driver_dir, exist_ok=True)
            
            # Get latest ChromeDriver version
            response = urllib.request.urlopen("https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
            latest_version = response.read().decode('utf-8').strip()
            logger.info(f"Latest ChromeDriver version: {latest_version}")
            
            # Determine system architecture
            system = platform.system().lower()
            if system == "windows":
                platform_name = "win32"
            elif system == "darwin":
                platform_name = "mac64"
            else:  # Linux
                platform_name = "linux64"
            
            # Download URL
            download_url = f"https://chromedriver.storage.googleapis.com/{latest_version}/chromedriver_{platform_name}.zip"
            logger.info(f"Downloading ChromeDriver from: {download_url}")
            
            # Download zip file
            zip_path = os.path.join(driver_dir, "chromedriver.zip")
            urllib.request.urlretrieve(download_url, zip_path)
            
            # Extract zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(driver_dir)
                
            # Set executable permissions on Unix
            if system != "windows":
                driver_path = os.path.join(driver_dir, "chromedriver")
                os.chmod(driver_path, 0o755)
            
            # Clean up zip file
            os.remove(zip_path)
            
            logger.info(f"ChromeDriver {latest_version} installed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to download ChromeDriver: {str(e)}")
            return False
    
    def close_browser(self):
        """Close the browser if it's open"""
        if self.browser:
            try:
                self.browser.quit()
                logger.info("Browser closed.")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
            finally:
                self.browser = None

    def crawl_url(self, url):
        """Crawl a URL and return the page content"""
        if not self.browser and not self._initialize_browser():
            return None

        try:
            logger.info(f"Crawling URL: {url}")
            self.browser.get(url)

            # Wait for page to load
            logger.info(f"Waiting {self.sleep_time} seconds for page to load...")
            time.sleep(self.sleep_time)

            # Get page data
            page_title = self.browser.title
            page_html = self.browser.page_source

            # Try to get meta description
            try:
                description_elem = self.browser.find_element("name", "description")
                page_description = description_elem.get_attribute("content")
            except:
                try:
                    # Try Open Graph description as fallback
                    description_elem = self.browser.find_element(
                        "property", "og:description"
                    )
                    page_description = description_elem.get_attribute("content")
                except:
                    page_description = f"Description for {page_title}"

            logger.info(f"Successfully crawled: {url}")
            logger.info(f"Title: {page_title}")

            return {
                "url": url,
                "title": page_title,
                "description": page_description,
                "html": page_html,
            }

        except TimeoutException:
            logger.error(f"Timeout error while crawling: {url}")
            return None
        except WebDriverException as e:
            logger.error(f"WebDriver error: {str(e)}")
            # Try to reinitialize browser
            self.close_browser()
            self._initialize_browser()
            return None
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return None
