from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException

import json
import os
import logging
from datetime import datetime

class Scraper:
    url = os.getenv('URL')
    OUTPUT_DIR = './output'
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    driver = None
    record = {}

    def __init__(self):
        self.start_session()


    def start_session(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        self.logger.info('Chrome session started')
        self.driver.get(self.url)
        self.logger.info('Scrapping initiated')
        winning_ticket_details = self.driver.find_element(By.XPATH,"//a[@class='btn btn-orange form-control linkShowWinningOutlets']")
        winning_ticket_details.click()

    def scrape(self):
        # date
        try:
            wait = WebDriverWait(self.driver, 10)
            date_ele = wait.until(EC.presence_of_element_located((By.XPATH, "//th[@class='drawDate']")))
            date_str = date_ele.text.replace(',', '')
            self.record["date"] = date_str
            date_str = " ".join(date_str.split(" ")[1:])
            date_format = "%d %b %Y"
            date_dir = datetime.strptime(date_str, date_format)
            date_dir = datetime.strftime(date_dir, '%Y%m%d')
        except NoSuchElementException:
            self.logger.info('Cannot load date')

        self.OUTPUT_DIR = f'{self.OUTPUT_DIR}/{date_dir}'
        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)

        # draw number
        try:
            draw_no_text = wait.until(EC.presence_of_element_located((By.XPATH, "//th[@class='drawNumber']")))
            self.record["draw_no"] = draw_no_text.text.split(" ")[2]
        except NoSuchElementException:
            self.logger.info('Cannot load draw number')

        # winning numbers
        self.record['winning_numbers'] = []
        for i in range(1, 7):
            xpath = f"//td[@class='win{i}']"
            winning_no = self.driver.find_element(By.XPATH, xpath).text
            self.record['winning_numbers'].append(winning_no)

        # additional number and group 1 prize
        self.record['additional_number'] = self.driver.find_element(By.XPATH, "//td[@class='additional']").text
        self.record['group_1_prize'] = self.driver.find_element(By.XPATH, "//td[@class='jackpotPrize']").text

        # winning shares
        self.record['winning_shares'] = []
        winning_shares_rows = self.driver.find_elements(By.XPATH, "//table[@class='table table-striped tableWinningShares']//tr")
        for row in winning_shares_rows[2::]:
            tds = row.find_elements(By.TAG_NAME, 'td')
            group = []
            for td in tds:
                group.append(td.text)
            self.record['winning_shares'].append(group)

        # winning outlets
        self.record['group_1_outlets'] = []
        self.record['group_2_outlets'] = []
        try:
            ul = self.driver.find_element(By.XPATH, "//div[@class='divWinningOutlets']/ul")
            outlets = ul.find_elements(By.XPATH, "./li")
            for outlet in outlets:
                self.record['group_1_outlets'].append(outlet.text)
        except WebDriverException:
            self.logger.info('No group 1 winner')

        try:
            ul = self.driver.find_elements(By.XPATH, "//div[@class='divWinningOutlets']/ul")
            if len(ul) > 0:
                if len(ul) > 1:
                    ul = ul[1]
                else:
                    ul = ul[0]
                outlets = ul.find_elements(By.XPATH, "./li")
                for outlet in outlets:
                    self.record['group_2_outlets'].append(outlet.text)
        except WebDriverException:
            self.logger.info('No group 2 winner')

        self.export_records()

    def export_records(self):
        # series = pd.Series(self.record, index=list(self.record.keys()))
        output_path = f'{self.OUTPUT_DIR}/records.json'
        # series.to_csv(output_path, index=False)
        with open(output_path, "w") as outfile:
            json.dump(self.record, outfile)


    def scrape_past_year(self):
        for i in range(104):
            self.OUTPUT_DIR = 'output'
            try:
                select = Select(self.driver.find_element(By.XPATH, "//select[@class='form-control selectDrawList']"))
                select.select_by_index(i)
                self.scrape()
            except WebDriverException as e:
                print('error', WebDriverException)

    def quit(self):
        if self.get_session_status():
            self.driver.quit()
            logging.info('Webdriver session successfully terminated')
        else:
            logging.info('Webdriver session does not exist')


def run_scraper():
    scraper = Scraper()
    scraper.start_session()
    scraper.scrape_past_year()
    # print(scraper.record)

run_scraper()

