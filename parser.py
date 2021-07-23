import requests_html
import sqlite3
from bs4 import BeautifulSoup
import urllib.request
from selenium import webdriver
import time
#...на всякий случай вдруг пригодится
class Proxy(object):
    def __init__(self, address, port, country, speed, delay):
        self.address = address
        self.port = port
        self.country = country
        self.speed = speed
        self.delay = delay

#...создание базы данных Sqlite
#...!добавить недостающие атрибуты
def createDb():
    connection = sqlite3.connect('proxy.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ProxyList
                    (Address TEXT UNIQUE, Port TEXT, Available TEXT DEFAULT('NO'))''')
    connection.commit()
    connection.close()



#...вывод существующей базы данны
def printDb():
    connection = sqlite3.connect('proxy.db')
    cursor = connection.cursor()
    records = cursor.execute("SELECT * FROM ProxyList")
    print('|...Address...|...port.....|...Available...|')
    for elem in cursor.fetchall():
        print(elem[0], '   ', elem[1], '   ', elem[2])
    connection.commit()
    connection.close()

#...вывод прокси с проверкой
def printProxy():
    with sqlite3.connect('proxy.db') as connection:
        cursor = connection.cursor()
        records = cursor.execute("SELECT * FROM ProxyList")
        for elem in cursor.fetchall():
            proxychecker(elem[0]+':'+elem[1])
        connection.commit()

#вставка списка прокси в базу данных
def insert(proxylist):
    with sqlite3.connect('proxy.db') as connection:
        cursor = connection.cursor()
        try:
            cursor.executemany("INSERT INTO ProxyList (Address, port) VALUES (?, ?)", proxylist)
            connection.commit()
        except Exception as e:
            print(e)

#...парсинг сайта https://free-proxy-list.net
#на странице содержит 20 записей, которые обновляются каждые 10 минут
def parsing_proxy1():
    proxylist = list()
    session = requests_html.HTMLSession()
    r = session.get('https://free-proxy-list.net/')
    r.html.render(timeout=20) # timeout=20 базово стоит 8, перестало хватать
    for i in range(1, 21):
        address = r.html.xpath('/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[1]/text()'.format(i))[0]
        port = r.html.xpath('/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[2]/text()'.format(i))[0]
        proxylist.append([address,port])
    insert(proxylist)



#...парсинг сайта http://foxtools.ru
#содержит 3 страницы ссылка на страницу http://foxtools.ru/Proxy?page='номер страницы'
def parsing_proxy2():
    proxylist = list()
    session = requests_html.HTMLSession()
    for i in ['1','2','3']:
        r = session.get('http://foxtools.ru/Proxy?page='+i)
        soup = BeautifulSoup(r.text, 'lxml')
        line = soup.find('table', id='theProxyList').find('tbody').find_all('tr')
        for tr in line:
            td = tr.find_all('td')
            address = td[1].text
            port = td[2].text
            proxylist.append([address,port])
    insert(proxylist)

#selenium
#...парсинг сайта https://spys.one/en/free-proxy-list/
#имеет несколько разделов с прокси
#стандартно отображает 30 записей, на сайте можно выбрать 500
#выбираем 500 записей
def parsing_proxy3():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # открытие без графического интерфейса
    browser = webdriver.Chrome(options=options)
    browser.get('https://spys.one/en/free-proxy-list/')
    button = browser.find_element_by_id('xpp').find_elements_by_tag_name('option')[5]
    button.click()
    time.sleep(10)
    proxylist = list()
    soup = BeautifulSoup(browser.page_source, 'lxml')
    line = soup.find('body').find_all('table')[1].find_all('tr')[3].find('table').find_all('tr')
    for i in range(1,500):
        address = (line[2*i].find_all('td')[0].find('font').text).split(':')[0]
        port = (line[2*i].find_all('td')[0].find('font').text).split(':')[1]
        proxylist.append([address,port])
    insert(proxylist)


#selenium
#...парсинг сайта https://advanced.name/ru/freeproxy
#переход по четырем страницам
def parsing_proxy4():
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')  # открытие без графического интерфейса
    browser = webdriver.Chrome(options=options)
    browser.get('https://advanced.name/ru/freeproxy')
    soup1 = BeautifulSoup(browser.page_source, 'lxml')
    number_of_pages = len(soup1.find('body').find_all('section')[1].find("ul", class_="pagination pagination-lg").find_all('li'))-2

    for i in range(0,number_of_pages - 1):
        button = browser.find_element_by_id('pricing').find_element_by_class_name("pagination.pagination-lg").find_elements_by_tag_name('li')[number_of_pages+1].find_element_by_tag_name('a')
        button.click()
        time.sleep(10)
        proxylist = list()
        soup = BeautifulSoup(browser.page_source, 'lxml')
        line = soup.find('body').find_all('section')[1].find("div", class_="table-responsive").find('table').find('tbody').find_all('tr')
        for tr in line:
            address = tr.find_all('td')[1].text
            port = tr.find_all('td')[2].text
            proxylist.append([address,port])
        insert(proxylist)



#парсинг сайта https://www.proxynova.com/proxy-server-list/
def parsing_proxy5():
    proxylist = list()
    session = requests_html.HTMLSession()
    r = session.get('https://www.proxynova.com/proxy-server-list/')
    r.html.render(timeout=20) # timeout=20 базово стоит 8, перестало хватать
    for i in range(1, 21):
        try:
            address = r.html.xpath('/html/body/div[3]/div[2]/table/tbody[1]/tr[{}]/td[1]/abbr/text()'.format(i))[1].replace(' ', '')
            port = r.html.xpath('/html/body/div[3]/div[2]/table/tbody[1]/tr[{}]/td[2]/text()'.format(i))[0].replace(' ', '')
        except Exception:
            pass
        proxylist.append([address,port])
    insert(proxylist)


#...проверяет прокси из бд, результат записывает в бд
def proxyCheck():
    with sqlite3.connect('proxy.db') as connection:
        cursor = connection.cursor()
        records = cursor.execute("SELECT * FROM ProxyList")
        list= cursor.fetchall()
        for elem in list:
            if proxychecker(elem[0]+':'+elem[1]):
                cursor.execute("""Update ProxyList set Available = 'YES' where Address = ?""",(elem[0],  ))
                connection.commit()

#проверяет отдельно взятую прокси
#обращение к сайту
def proxychecker(proxy):
    for site in ['http://www.google.com','https://yandex.ru','https://www.facebook.com']:
        address = 'http://' + proxy
        proxy_support = urllib.request.ProxyHandler({'http' : address})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        req = urllib.request.Request(site)
        #req.add_header("User-Agent", random.choice(useragents)) #имитация разных устройств
        try:
            urllib.request.urlopen(req, timeout=60)
        except:
            return False
    return True
#createDb()
#parsing_proxy1()

#parsing_proxy2()
#parsing_proxy3()
parsing_proxy4()
#parsing_proxy5()
#printDb()
#proxyCheck()

#print(proxychecker('190.108.93.87:999'))