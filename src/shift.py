import yaml
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import bs4
import re
import datetime

from PIL import Image
import sys
import subprocess
import csv
import logging
import traceback

# local
import mail

def main():
    print('start...')    

    with open('../config/config.yml') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    csvList = []
    for i in range(1):
        csvList.extend(getShiftData(config, i))
        
        # printShift(config)

    for row in csvList:
        print(row[0] + "," + row[1])

# 画面遷移しスクリーンショットを保存
def getShiftData(config, placeId):
    
    options = webdriver.ChromeOptions()
    options.add_argument('--kiosk')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get('https://airshift.jp/sft/dailyshift')

        # ログイン画面
        driver.find_element_by_name('username').send_keys(config['ID'])
        driver.find_element_by_name('password').send_keys(config['PASS'])
        driver.find_element_by_id('command').submit()

        time.sleep(1)

        # 拠点選択画面
        elements = driver.find_elements_by_class_name('searchTarget')
        elements[placeId].click()

        # デイリーレポート画面
        # url = 'https://airshift.jp/sft/dailyshift'
        
        # dayFlg = False
        # if len(sys.argv) > 1:
        #     dayFlg = True
        #     url = 'https://airshift.jp/sft/dailyshift/' + sys.argv[1]

    
        driver.get('https://airshift.jp/sft/monthlyshift')
        time.sleep(2)
        # select = Select(driver.find_element_by_name('filter-staff'))
        # select.select_by_value('fixed')

        driver.find_elements_by_class_name('content___vochnIhs')[0].click()
        time.sleep(4)

        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')
        
        print(soup)

        names = soup.findAll('div',class_="name___1yaaRDba")
        siteList = ["渋谷","難波","新宿"]
        
        csvlist = []
        
        for name in names:
            csvlist.append([name.text.replace('z', '').replace('(AI)', ''),siteList[placeId]])

        driver.save_screenshot(config['FILE'])
        
        dayFlg = True
        
        if not dayFlg:
            sendSlack(config, siteList[placeId])
            print("take photo")
            time.sleep(20)

        return csvlist
        
    except Exception as e:
        logging.error(traceback.format_exc())
        return [[]]
    finally:
        driver.quit()

def printShift(config):
    monochrome(config)
    sendGmailAttach(config)

# 画像を白黒化
def monochrome(config):
    img = Image.open(config['FILE'])
    img_gray = img.convert('L')
    img_gray.save(config['FILE'])


def sendSlack(config, fileName):
    subprocess.call(["slackcat", "--channel", config['SLACK_CHANNEL'], "--filename",fileName + ".png", config['FILE']])

if __name__ == '__main__':
    main()
