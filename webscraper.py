# use Selenium to access website and scrape data from
# the 1st 2 html tags with class 'analytic-item'

from datetime import datetime
import os
import time
from zoneinfo import ZoneInfo
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import schedule
from dotenv import load_dotenv

# load dotenv file
load_dotenv()

# set env vars
website_url = os.environ['WEBSITE_URL']
login_username = os.environ['USERNAME']
login_password = os.environ['PASSWORD']
mailgun_api_key = os.environ['MAILGUN_API_KEY']
mailgun_url = os.environ['MAILGUN_URL']
email_from_str = os.environ['EMAIL_FROM']
email_to_str = os.environ['EMAIL_TO']

# set up chrome options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")

# set up chrome driver
# ! NB: adjust accordingly to your own path, or use webdriver_manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def send_email(res_str: str):
    # email data with mailgun API
    sg_curr_time = datetime.now().astimezone(tz=ZoneInfo("Singapore")).strftime("%Y-%m-%d %H:%M:%S")
    return requests.post(
        mailgun_url + '/messages',
        auth=('api', mailgun_api_key),
        data={'from': email_from_str,
              'to': email_to_str,
              'subject': f'NB User Count {sg_curr_time}',
              'text': res_str})


def scrape_and_email():
    # access the website
    driver.get(website_url)

    # input username and password if available
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "login-page")))
        print('Login page found')
        username = driver.find_element(by=By.NAME, value="usernameOrEmailAddress")
        password = driver.find_element(by=By.ID, value="Password")
        username.send_keys(login_username)
        password.send_keys(login_password)
        driver.find_element(by=By.ID, value="LoginButton").click()
    except:
        print('No login page, skipping...')
        pass

    # wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "analytic-item")))
    print('Homepage found')

    # find the html tags
    analytic_items = driver.find_elements(by=By.CLASS_NAME, value="analytic-item")

    # store data as string, delimited by newline
    res = ''

    # insert first 2 items of analytics-item
    for item in analytic_items[:2]:
        label = item.find_element(by=By.CLASS_NAME, value="tag-name").text
        value = item.find_element(by=By.CLASS_NAME, value="tag-value").text
        res += f'{label}: {value}\n'

    # navigate to the "Community" page
    driver.get(f"{website_url}/Community")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "CommunityTable")))
    print('Community page found')
    # get text from class card-footer-item of community_list
    community_list_footer = driver.find_element(
        by=By.ID, value="CommunityListContent").find_element(
        by=By.CLASS_NAME, value="card-footer-item")
    # get data in div in community_list_footer
    community_list_footer_data = community_list_footer.find_element(by=By.TAG_NAME, value="div").text

    # insert community_list_footer_data
    res += f"Communities: {community_list_footer_data.split('of ', 1)[1].split(' entries', 1)[0]}\n"

    # print the data
    print(res)

    # close the driver
    driver.close()

    # send email
    send_email(res)


def schedule_task():
    # ! adjust schedule according to timezone
    schedule.every().day.at("00:01").do(scrape_and_email)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    schedule_task()
