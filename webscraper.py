# use Selenium to access website and scrape data from
# the 1st 2 html tags with class 'analytic-item'

from datetime import datetime
import logging
import os
from zoneinfo import ZoneInfo
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
from dotenv import load_dotenv

# load dotenv file
load_dotenv()

# create logs/ dir if not exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# init logging
logger = logging.getLogger('nb-webscraper')
logger.setLevel(logging.INFO)
info_fh = logging.FileHandler('logs/nb-webscraper.log')
info_fh.setLevel(logging.INFO)
info_fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(info_fh)
error_fh = logging.FileHandler('logs/nb-webscraper-error.log')
error_fh.setLevel(logging.ERROR)
error_fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(error_fh)
# for errors, log to stderr as well
error_sh = logging.StreamHandler()
error_sh.setLevel(logging.ERROR)
error_sh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(error_sh)

# set env vars
website_url = os.environ['WEBSITE_URL']
login_username = os.environ['USERNAME']
login_password = os.environ['PASSWORD']
mailgun_api_key = os.environ['MAILGUN_API_KEY']
mailgun_url = os.environ['MAILGUN_URL']
email_from_str = os.environ['EMAIL_FROM']
email_to_str = os.environ['EMAIL_TO']
email_cc_str = os.getenv('EMAIL_CC')  # optional field

# set up chrome options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")


def send_email(res_str: str):
    # email data with mailgun API
    sg_curr_time = datetime.now().astimezone(tz=ZoneInfo("Singapore")).strftime("%Y-%m-%d %H:%M:%S")
    return requests.post(
        mailgun_url + '/messages',
        auth=('api', mailgun_api_key),
        data={'from': email_from_str,
              'to': email_to_str,
              'cc': email_cc_str,
              'subject': f'NB User Count {sg_curr_time}',
              'text': res_str})


def scrape_and_email():
    # set up chrome driver
    # ! NB: adjust accordingly to your own path, or use webdriver_manager
    driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=chrome_options)
    # access the website
    try:
        driver.get(website_url)
    except Exception as e:
        logger.error(f'Error accessing website: {e}')
        return

    # input username and password if available
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "login-page")))
        username = driver.find_element(by=By.NAME, value="usernameOrEmailAddress")
        password = driver.find_element(by=By.ID, value="Password")
        username.send_keys(login_username)
        password.send_keys(login_password)
        driver.find_element(by=By.ID, value="LoginButton").click()
    except:
        logger.info('No login page, skipping...')
        pass

    # wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "analytic-item")))

    # find the html tags
    analytic_items = driver.find_elements(by=By.CLASS_NAME, value="analytic-item")

    # store data as string, delimited by newline
    res = ''
    total_value = 0

    # insert first 2 items of analytics-item
    for item in analytic_items[:2]:
        label = item.find_element(by=By.CLASS_NAME, value="tag-name").text
        value = item.find_element(by=By.CLASS_NAME, value="tag-value").text
        res += f'{label}: {value}\n'
        total_value += int(value)

    # insert total value
    res += f'Total: {total_value}\n'

    # navigate to the "Community" page
    try:
        driver.get(f"{website_url}/Community")
    except Exception as e:
        logger.error(f'Error accessing Community page: {e}')
        return

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "CommunityTable")))
    # get text from class card-footer-item of community_list
    community_list_footer = driver.find_element(
        by=By.ID, value="CommunityListContent").find_element(
        by=By.CLASS_NAME, value="card-footer-item")
    # get data in div in community_list_footer
    community_list_footer_data = community_list_footer.find_element(by=By.TAG_NAME, value="div").text

    # insert community_list_footer_data
    res += f"Communities: {community_list_footer_data.split('of ', 1)[1].split(' entries', 1)[0]}\n"

    # print the data
    logger.info(res.replace('\n', ', '))

    # close the driver
    driver.close()

    # send email
    try:
        send_email(res)
    except Exception as e:
        logger.error(f'Error sending email: {e}')
        return
    logger.info('Email sent')


if __name__ == '__main__':
    scrape_and_email()
