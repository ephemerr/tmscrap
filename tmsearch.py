from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'")
driver = webdriver.Chrome(options=chrome_options)

detailsuche = "https://www.transfermarkt.com/detailsuche/spielerdetail/suche"

driver.implicitly_wait(10)

driver.get(detailsuche)

frame = driver.find_element(By.CSS_SELECTOR, "#sp_message_container_764226 > iframe")
driver.switch_to.frame(frame)

driver.find_element(By.XPATH,'//button[@title="ACCEPT ALL"]').click()

last_name = driver.find_element(By.CSS_SELECTOR, "#Detailsuche_name")
ActionChains(driver).scroll_to_element(last_name).perform()
last_name.send_keys("Pinyaev")

submit_search = driver.find_element(By.CSS_SELECTOR, "input.button[value='Submit search']")

!rm tm_screenshot.png
driver.save_screenshot("tm_screenshot.png")
!op tm_screenshot.png

