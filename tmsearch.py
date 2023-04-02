from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

def get_tm_profile_by_name_and_age(surname, age, num_of_tries=3):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'")
    driver = webdriver.Chrome(options=chrome_options)

    detailsuche = "https://www.transfermarkt.com/detailsuche/spielerdetail/suche"

    driver.implicitly_wait(5)

    for i in range(0,num_of_tries):
        driver.get(detailsuche)
        if driver.title != "Error | Transfermarkt":
            break;

    html = driver.find_element(By.CSS_SELECTOR, "html")

    frame = driver.find_element(By.CSS_SELECTOR, "#sp_message_container_764226 > iframe")
    driver.switch_to.frame(frame)

    driver.find_element(By.XPATH,'//button[@title="ACCEPT ALL"]').click()

    last_name = driver.find_element(By.CSS_SELECTOR, "#Detailsuche_name")
    ActionChains(driver).scroll_to_element(last_name).perform()

    last_name.send_keys(surname)

    minAlter = driver.find_element(By.XPATH,'//input[@id="minAlter"]')
    maxAlter = driver.find_element(By.XPATH,'//input[@id="maxAlter"]')

    # amountAlter = driver.find_element(By.XPATH,'//input[@id="amountAlter"]')
    # ActionChains(driver).scroll_to_element(amountAlter).perform()

    driver.execute_script("arguments[0].setAttribute('value',arguments[1])",minAlter, age)
    driver.execute_script("arguments[0].setAttribute('value',arguments[1])",maxAlter, age)


    driver.find_element(By.CSS_SELECTOR, "input.button[value='Submit search']").click()

    profile_link = ""
    for i in range(0,num_of_tries):
        try:
            profile_link = driver.find_element(By.XPATH,'//table[@class="items"]/tbody/tr[1]/td[2]/table/tbody/tr//td[2]/a').get_attribute("href")
        except:
            if driver.title != "Error | Transfermarkt":
                print("Search results are empty")
                break;
            print("Search results not obtained")
            time.wait(2);
            html.send_keys(Keys.COMMAND + r)
        break

    return  profile_link


# !rm tm_screenshot.png
# driver.save_screenshot("tm_screenshot.png")
# !op tm_screenshot.png

# html.send_keys(Keys.PAGE_DOWN)

# html.send_keys(Keys.PAGE_UP)

get_tm_profile_by_name_and_age("Kozlovi",22)
