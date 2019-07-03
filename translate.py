from selenium import webdriver
import time
from bs4 import BeautifulSoup
import json
import config


class Translate:
    def __init__(self, ID, PWD, HPAGE):
        self.origin_words = []
        self.translated_words = []
        self.ID = ID
        self.PWD = PWD
        self.HPAGE = HPAGE
        with open('app_name.json') as f:
            self.data = json.load(f)

        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # options.add_argument('window-size=1920x1080')
        # options.add_argument("disable-gpu")
        #
        # self.driver = webdriver.Chrome('chrome/chromedriver_74', options=options)
        self.driver = webdriver.Chrome('chrome/chromedriver_74')

        return

    def login_to_confluence(self):
        # confluence에 로그인을 한다
        # 아이디와 패스워드를 작성하고
        # 로그인 버튼을 클릭한다
        self.driver.get(self.HPAGE + '/pages/viewpage.action?pageId=625781')
        self.driver.implicitly_wait(1)
        id = self.driver.find_element_by_xpath('''//*[@id="os_username"]''')
        id.send_keys(self.ID)
        pwd = self.driver.find_element_by_xpath('''//*[@id="os_password"]''')
        pwd.send_keys(self.PWD)
        self.driver.find_element_by_xpath('''//*[@id="loginButton"]''').click()
        self.driver.implicitly_wait(1)

    def process_work(self):
        # 03. 패키지요청서를 클릭하고
        # 그 안에서 a tag들을 가지고 와서 url_list에 담는다
        self.driver.find_element_by_xpath('''//*[@id="childrenspan4195615-0"]/a''').click()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        atags = soup.find("ul", {'id': 'child_ul4195615-1'}).find_all("a")
        url_list = [a['href'] for a in atags if "#" not in a['href']]

        # url_list로 화면들을 iterate 하면서 번역할 앱 이름들이 있는지 확인하고
        # 있으면 번역을 진행한다
        for i, href in enumerate(url_list):
            self.driver.get(self.HPAGE + href)
            self.driver.implicitly_wait(2)
            soup = BeautifulSoup(self.driver.page_source, "lxml")

            # 해당 페이지에 릴리즈 노트가 있고 번역해야할 앱 이름들이 있으면 번역을 실시한다
            # 다음페이지로 넘어가기 전에 리스트를 비워준다
            if self.check_translation_needed(soup):
                self.translate_and_change_words()
            self.origin_words = []
            self.translated_words = []

        time.sleep(6)
        self.driver.quit()

    def check_translation_needed(self, soup):
        has_release = False

        # 모든 p 들을 찾고 그 안에
        # 릴리즈 노트라는 영역이 있는지 체크한다
        # 있으면 단어 수집을 시작하고 아니면 넘어간다
        ps = soup.find(id="main-content").find_all("p")
        for p in ps[::-1]:
            if "릴리즈" in p.text:
                has_release = True
                break

        # 릴리즈 노트 있다면 번역해야할 contents들 있는지 체크한다
        # empty라면 넘어간다
        # 여러 table들 중에 앱-한글 이라고 쓰여져 있는 table만 가지고 온다(해당 테이블만 번역이 필요하기 때문)
        if has_release:
            table = soup.find_all('table', {"class": "confluenceTable"})
            table_one = ""
            for t in table:
                if ("모델 정보" not in str(t) and "버그" not in str(t)) and ("앱" in str(t) and "한글" in str(t)):
                    table_one = t
                    # 모든 tr들을 가지고 오고
                    # tr empty 하면 분석 진행하지 않는다
                    trs = table_one.findAll('tr')
                    if len(trs[1:]) > 1 or trs[1].findAll('td')[0].text.strip() != "":
                        for tr in trs[1:]:
                            self.origin_words.append(tr.findAll('td')[0].text.rstrip())
                    else:
                        return False

            return False if (table_one == "") else True
        else:
            return False

    # 번역을 하고
    # 그 이후에 편집을 통해 단어들을 대체한다
    def translate_and_change_words(self):
        self.make_translation()

        time.sleep(1)
        self.driver.execute_script("document.getElementById('editPageLink').click()")
        self.driver.switch_to.frame(self.driver.find_element_by_id('wysiwygTextarea_ifr'))
        self.change_words()
        self.driver.switch_to.default_content()

        # 저장을 클릭한다
        # self.driver.find_element_by_xpath('''//*[@id="rte-button-publish"]''').click()

    # json에서 단어들을 가지고 와서
    # translated_words 라는 list 에 담는다
    def make_translation(self):
        for word in self.origin_words:
            if word in self.data:
                self.translated_words.append(self.data[word])
            else:
                self.translated_words.append(word)

    # 편집 페이지에 들어가서 단어들을 대체 한다
    def change_words(self):
        try:
            # table들을 찾고 번역이 필요한 table을 찾는다
            table = self.driver.find_elements_by_class_name('confluenceTable')

            idx = 0
            for t in table:
                table_to_change = "NOT"
                indexErr = False

                th = ""
                try:
                    th = t.find_elements_by_class_name('confluenceTh')[0]
                    cond2_1 = ("모델 정보" not in th.text and "버그" not in th.text)
                    cond2_2 = ("앱" in th.text and "한글" in th.text)
                except IndexError:
                    indexErr = True
                td = t.find_elements_by_class_name('confluenceTd')[0]

                # table마다 th 혹은 td로 시작하는 것이 달라서 다르게 표현을 했다
                cond1_1 = ("모델 정보" not in td.text and "버그" not in td.text)
                cond1_2 = ("앱" in td.text and "한글" in td.text)
                if indexErr and cond1_1 and cond1_2:
                    table_to_change = "TD"
                elif cond2_1 and cond2_2:
                    table_to_change = "TH"


                # 번역이 필요한 table 이면 기존에 있던 list에서 단어들을 가지고 와서 대체한다
                # css selector를 찾고
                # js execute를 사용해서 단어들을 대체한다
                if table_to_change != "NOT":
                    for tr in t.find_elements_by_tag_name('tr')[1:]:
                        td = tr.find_elements_by_tag_name('td')[1]
                        self.driver.execute_script('''arguments[0].innerHTML=arguments[1]''', td, self.translated_words[idx])
                        # selector = self.driver.execute_script(self.JS_BUILD_CSS_SELECTOR, td)
                        # self.driver.execute_script('''document.querySelector(arguments[0]).innerHTML=arguments[1]''', selector, )
                        idx += 1
        except IOError:
            print("IO ERROR")
        except ModuleNotFoundError:
            print("NO MODULE")


if __name__ == "__main__":
    start_time = time.time()
    trans = Translate(config.__ID, config.__PASSWORD, config.__HOMEPAGE)
    trans.login_to_confluence()
    trans.process_work()
    print("--- %s seconds ---" % (time.time() - start_time))
