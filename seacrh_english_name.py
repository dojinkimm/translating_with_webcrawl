from selenium import webdriver
from bs4 import BeautifulSoup
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config


class SearchEngName:
    def __init__(self, g_id, g_pwd):
        self.origin_words = []
        self.translated_words = []
        self.g_id = g_id
        self.g_pwd = g_pwd
        # with open('app_name.json') as f:
        #     self.data = json.load(f)

        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # options.add_argument('window-size=1920x1080')
        # options.add_argument("disable-gpu")
        #
        # self.driver = webdriver.Chrome('chrome/chromedriver_74', options=options)
        self.driver = webdriver.Chrome('chrome/chromedriver_74')

        return

    def process_work(self):
        self.app_name_to_find()
        self.go_play_store()
        self.find_eng_name()
        self.driver.quit()



    def app_name_to_find(self):
        print("Type app name you want to to make translation")
        print("(The program begins if you click 'q' or 'Q' or '끝')")
        while True:
            key = input("App Name: ")
            if key == "q" or key == "Q" or key == '끝':
                break
            self.origin_words.append(key)
        print("Now I will find English Name")

    def go_play_store(self):
        self.driver.get('https://play.google.com/store/apps')
        self.driver.implicitly_wait(1)

    def find_eng_name(self):
        for word in self.origin_words:
            self.driver.get('https://play.google.com/store/search?q='+word+'&hl=en')
            apps = self.driver.find_elements_by_class_name('details')






if __name__ == "__main__":
    search = SearchEngName(config._G_ID, config._G_PWD)
    search.process_work()

