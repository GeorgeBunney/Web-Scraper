from pickle import TRUE
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from sqlalchemy import create_engine, true
import uuid
import json
import urllib.request
import boto3
import csv

class web_scraper:
    def __init__(self): 
        print('__init__')
        print('1')
        options = webdriver.ChromeOptions()
        print('2')
        options.add_argument('--ignore-ssl-errors=yes')
        print('4')
        options.add_argument('--ignore-certificate-errors')
        print('5')
        self.driver = webdriver.Remote(
        command_executor='http://172.17.0.2:4444/wd/hub',
        options=options
        )
        print('6')
        self.page_number=1
        self.engine=create_engine(f"{'postgresql'}+{'psycopg2'}://{'postgres'}:{'24316875'}@{'database-1.cvzi0tpnjw4c.eu-west-2.rds.amazonaws.com'}:{5432}/{'postgres'}")
        self.author_url_list=[]
        
    def _start(self):
        print('start')
        self.open_page("https://www.audible.co.uk/search?searchAuthor=&sort=popularity-rank&ref=a_search_c1_sort_2&pf_rd_p=56a637ed-6f1b-4758-8d02-5bcd48128c1f&pf_rd_r=D4C7GBCPF668JV1MN0AC")
        self.click('//*[@id="truste-consent-button"]')

    def open_page(self, url):
        print('open page')
        '''opens the page at the provided url'''
        try:
            self.driver.get(url)
            sleep(1)
        except:
            print('open_page failed')
            pass

    def click(self, xpath):
        print('click')
        '''clicks on a button at the provided xpath or passes if there is no button'''
        try:
            button = self.driver.find_element(By.XPATH, xpath)
            button.click()
            sleep(1)
        except:
            print('click failed')
            pass
        

    def scroll(self,magnitude): 
        print('scroll')
        '''scrolls the page to a given possition'''
        try:
            self.driver.execute_script(f"window.scrollTo(0, {magnitude})") 
            sleep(1)
        except:
            print('scroll failed')
            pass

    def get_href_attribute(self, xpath):
        print('get_href_attribute')
        '''retrieves a href attribute from an x path position'''
        try:
            return self.driver.find_element(By.XPATH, xpath).get_attribute('href')
        except:
            pass

    def _next_page(self):
        print('_next_page')
        button_possition = 1
        while TRUE:
            try:
                self.driver.find_element(By.XPATH, f'/html/body/div[1]/div[5]/div[5]/div/div[2]/div[5]/form/div/div/div[2]/div/span/ul/li[{button_possition}]')
                button_possition = button_possition +1
            except:
                break
        button_possition = button_possition -1
        self.click(f'/html/body/div[1]/div[5]/div[5]/div/div[2]/div[5]/form/div/div/div[2]/div/span/ul/li[{button_possition}]/span/a')

    def _prev_page(self):
        try:
            self.click('/html/body/div[1]/div[5]/div[5]/div/div[2]/div[5]/form/div/div/div[2]/div/span/ul/li[1]/span/a')
        except:
            print('no previos page')
            pass

    def _get_author_urls(self,author_quantity):
        print('_get_author_urls')
        book_number=1
        while TRUE:
            while book_number<21:
                book_author_number = 1
                try:
                    print('url try')
                    url = self.get_href_attribute(f'/html/body/div[1]/div[5]/div[5]/div/div[2]/div[4]/div/div/span/ul/div/li[{book_number}]/div/div[1]/div/div[2]/div/div/span/ul/li[2]/span/a')
                    print('url success')
                    if type(url) != str:
                        try:
                            url = self.get_href_attribute(f'/html/body/div[1]/div[5]/div[5]/div/div[2]/div[4]/div/div/span/ul/div/li[{book_number}]/div/div[1]/div/div[2]/div/div/span/ul/li[3]/span/a')
                        except:
                            pass
                    book_number=book_number+1
                    try:
                        if url.split("/")[4] not in ''.join(self.author_url_list):
                            self.author_url_list.append(url)
                    except:
                        if url.split("=")[1] not in ''.join(self.author_url_list):
                            self.author_url_list.append(url)
                    book_author_number = book_author_number + 1
                except:
                    print('url break')
                    break

                if author_quantity <= len(self.author_url_list):
                    break
            print(self.author_url_list)
            print(len(self.author_url_list))
            book_number=1
            if author_quantity <= len(self.author_url_list):
                print('finished getting urls')

                break
            self._next_page() 
            sleep(1)

    def _author_info_upload(self, id, name, category_list, author_uuid, picture_location):
        print('_author_info_upload')
        if self.engine.execute(f"""SELECT * FROM author_info WHERE id = '{id}' """).fetchall() == []:
            print(f'added {name}')
            self.engine.execute(f"""INSERT INTO author_info (id, name, uuid, picture_location) 
                                   VALUES ('{id.replace("'","")}', '{name.replace("'","")}', '{author_uuid.replace("'","")}', '{picture_location.replace("'","")}');""") 
            for category_list in category_list:
                self.engine.execute(f"""INSERT INTO categories (uuid, category) 
                                    VALUES ('{author_uuid.replace("'","")}', '{category_list.replace("'","")}');""")     

    def _get_book_info(self):
        print('_get_book_info')
        try:
            self.click('/html/body/div[1]/div[8]/div[11]/div/div[1]/a')
        except:
            pass


    def _get_author_info(self,author_quantity):
        print('_get_author_info')
        self._start()
        self._get_author_urls(author_quantity)
        author_info={}
        with open('new_user_credentials.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                access_key=row['Access key ID']
                secret_key=row['Secret access key']
        s3=boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        for url in self.author_url_list:
            self.open_page(url)
            category_list=[]

            try:
                name=self.driver.find_element(By.XPATH, '/html/body/div[1]/div[8]/div[2]/div[2]/div/div/div/div/div/div[4]/h1').text
                n=1
                while TRUE:
                    try:
                        category=self.driver.find_element(By.XPATH, f'/html/body/div[1]/div[8]/div[2]/div[2]/div/div/div/div/div/div[5]/a[{str(n)}]/span').text
                        category_list.append(category)
                    except:
                        break
                    n=n+1
            except:
                name=self.driver.find_element(By.XPATH, '/html/body/div[1]/div[5]/div[2]/div/h1/span').text
                name=name.replace('"','')
            n=0
            pre_id=name.replace("'","")
            

            while TRUE:
                if pre_id in author_info:
                    n=n+1
                else:
                    id=pre_id + str(n)
                    break
            #retriving author pictures from the website then uploading them to s3
            try:
                picture_xpath=self.driver.find_element(By.XPATH, '/html/body/div[1]/div[8]/div[2]/div[2]/div/div/div/div/div/div[1]/img')
                picture_url=picture_xpath.get_attribute('src')
                picture_name=f"{id}.jpg"
                urllib.request.urlretrieve(picture_url, picture_name)
                print('recieved picture')
                s3.upload_file(picture_name,'webscraper7890' , id)
                print('picture uploaded')
                picture_location=f'https://webscraper7890.s3.eu-west-2.amazonaws.com/{id}'
            except:
                picture_location='apple'
            #genirating author uuid
            #Web_scraping/images/Richard Osman0.jpg
            #book_info = self._get_book_info()
            
            author_uuid=str(uuid.uuid4())
            author_info[id]={"name":name,"categorys":category_list,"uuid":author_uuid,"picture":picture_location}
            self._author_info_upload(id, name, category_list, author_uuid, picture_location)



        f=open("data.json","w")
        json.dump(author_info,f)
        f.close()
        s3.upload_file("data.json",'webscraper7890' , 'data')


print('starting')
test=web_scraper()
test._get_author_info(10)
