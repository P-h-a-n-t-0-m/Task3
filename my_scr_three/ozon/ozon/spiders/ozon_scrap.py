from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import scrapy
import time
import pandas as pd
from scrapy_selenium import SeleniumRequest
from tabulate import tabulate


#####################################
# Используется Selenium для win64
# при необходимости заменить для нужной OC
# пути my_scr_three\ozon\ozon\chromedriver.exe , my_scr_three\ozon\ozon\spiders\Selenium\chromedriver.exe
#####################################

class OzonScrap(scrapy.Spider):
    name = "ozon_scrap"
    driver = None
    chrome_options = None
    s = None
    system_version_and = []
    system_version_ios = []

    def __init__(self, *a, **kw):
        super(OzonScrap, self).__init__(*a, **kw)
        self.chrome_options = Options()
        self.chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

        # chrome_options.headless = True
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        self.s = Service(r'Selenium\chromedriver.exe')

    def the_end_result(self):
        if len(self.system_version_ios) == 0:
            df = pd.DataFrame(self.system_version_and)
            df.sort_values('Operating system version', ascending=False, inplace=True)
            ress = tabulate(df, headers='keys', tablefmt='psql')
            with open('res.txt', 'w') as file:
                file.write(ress)
            exit(0)
        elif len(self.system_version_and) == 0:
            df2 = pd.DataFrame(self.system_version_ios)
            df2.sort_values('Operating system version', ascending=False, inplace=True)
            ress = tabulate(df2, headers='keys', tablefmt='psql')
            with open('res.txt', 'w') as file:
                file.write(ress)
            exit(0)
        else:
            df = pd.DataFrame(self.system_version_and)
            df2 = pd.DataFrame(self.system_version_ios)

            df.sort_values('Operating system version', ascending=False, inplace=True)

            df2.sort_values('Operating system version', ascending=False, inplace=True)

            res = df.append(df2)
            ress = tabulate(res, headers='keys', tablefmt='psql')
            with open('res.txt', 'w') as file:
                file.write(ress)
            exit(0)

    def start_requests(self):
        url = 'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating'
        yield SeleniumRequest(url=url, callback=self.parse, wait_time=15)

    def parse(self, response, **kwargs):
        response.request.meta['driver'].close()
        i1 = 1
        for _ in range(279):
            main_driver = response.request.meta['driver']
            main_driver = webdriver.Chrome(service=self.s, options=self.chrome_options)
            main_driver.get(
                f"https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?page={i1}&sorting=rating&tf_state=JcSKdhsY_KVMSAGQCqj6O_I6SrpVNzVH-99EdH4CCytJ2UqL")
            time.sleep(15)
            try:
                description = main_driver.find_elements(By.XPATH,
                                                        "//div[@class='k5u']/div[@class='s4k ks5']/div[2]/div[1]/span[@class='d3z z3d d7z tsBodyM']")
            except Exception:
                time.sleep(2)
                main_driver.close()
                main_driver = webdriver.Chrome(service=self.s, options=self.chrome_options)
                main_driver.get(
                    f"https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?page={i1}&sorting=rating&tf_state=JcSKdhsY_KVMSAGQCqj6O_I6SrpVNzVH-99EdH4CCytJ2UqL")
                time.sleep(10)
                description = main_driver.find_elements(By.XPATH,
                                                        "//div[@class='k5u']/div[@class='s4k ks5']/div[2]/div[1]/span[@class='d3z z3d d7z tsBodyM']")

            all_url = main_driver.find_elements(By.XPATH,
                                                "//div[@class='k5u']/div[@class='s4k ks5']/div[2]/div[1]/a")
            for one in range(len(description)):
                key_value = description[one].text.split('\n')
                if 'Тип: Смартфон' in key_value:
                    url = f"{all_url[one].get_attribute('href')}"
                    driver = webdriver.Chrome(service=self.s, options=self.chrome_options)
                    driver.get(url)
                    time.sleep(10)
                    try:

                        try:
                            name = driver.find_element(By.XPATH, '//div[@class="m2z zm8 zm6"]//div[2]//h1').text
                        except Exception:
                            time.sleep(2)
                            driver.close()
                            driver = webdriver.Chrome(service=self.s, options=self.chrome_options)
                            driver.get(url)
                            time.sleep(10)
                            name = driver.find_element(By.XPATH, '//div[@class="m2z zm8 zm6"]//div[2]//h1').text

                        a = driver.find_element(By.XPATH, '//div[@id="section-characteristics"]//div[@class=""]')
                        r = a.text.split('\n')
                        ios = 'Версия iOS'
                        android = 'Версия Android'

                        if ios in r:
                            ind = r.index(ios)
                            if (len(self.system_version_and) + len(self.system_version_ios)) == 100:
                                self.the_end_result()
                            else:
                                syst_i = str(r[ind + 1])
                                syst_i = syst_i.replace('iOS ', '')
                                self.system_version_ios.append(
                                    {"Model name": str(name), "Type of system": "IOS",
                                     "Operating system version": int(syst_i)})
                        elif android in r:
                            ind = r.index(android)
                            if (len(self.system_version_and) + len(self.system_version_ios)) == 100:
                                self.the_end_result()
                            else:
                                syst_a = str(r[ind + 1])
                                syst_a = syst_a.replace('Android ', '')
                                syst_a = syst_a.replace('.x', '')
                                self.system_version_and.append(
                                    {"Model name": name, "Type of system": "Android",
                                     "Operating system version": int(syst_a)})
                    except Exception as e:
                        pass
                    finally:
                        driver.close()
            i1 = i1 + 1
            main_driver.close()
        if (len(self.system_version_and) + len(self.system_version_ios)) < 100:
            self.the_end_result()
