import requests_html
from bs4 import BeautifulSoup
import urllib.request
from selenium import webdriver
import time
from datetime import datetime
from dbWork import insert

#...парсинг сайта https://free-proxy-list.net
#на странице содержит 20 записей, которые обновляются каждые 10 минут
def parsing_proxy1():

    session = requests_html.HTMLSession()
    r = session.get('https://free-proxy-list.net/')
    r.html.render(timeout=20) # timeout=20 базово стоит 8, перестало хватать
    for i in range(1, 21):
        proxylist = list()
        address = r.html.xpath('/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[1]/text()'.format(i))[0]
        port = r.html.xpath('/html/body/section[1]/div/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[2]/text()'.format(i))[0]
        proxylist.append([address + ':' + port, get_time()])
        insert(proxylist)



#...парсинг сайта http://foxtools.ru
#содержит 3 страницы ссылка на страницу http://foxtools.ru/Proxy?page='номер страницы'
def parsing_proxy2():
    session = requests_html.HTMLSession()
    for i in ['1','2','3']:
        proxylist = list()
        r = session.get('http://foxtools.ru/Proxy?page='+i)
        soup = BeautifulSoup(r.text, 'lxml')
        line = soup.find('table', id='theProxyList').find('tbody').find_all('tr')
        for tr in line:
            td = tr.find_all('td')
            address = td[1].text
            port = td[2].text
            proxylist.append([address + ':' + port,get_time()])
        insert(proxylist)

#selenium
#...парсинг сайта https://spys.one/en/free-proxy-list/
#имеет несколько разделов с прокси
#стандартно отображает 30 записей, на сайте можно выбрать 500
#нет смысла брать больше 60, дальше нерабочие
def parsing_proxy3():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # открытие без графического интерфейса
    browser = webdriver.Chrome(options=options)
    browser.get('https://spys.one/en/free-proxy-list/')
    button = browser.find_element_by_id('xpp').find_elements_by_tag_name('option')[5]
    button.click()
    time.sleep(10)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    line = soup.find('body').find_all('table')[1].find_all('tr')[3].find('table').find_all('tr')
    for i in range(1,60):
        proxylist = list()
        address = (line[2*i].find_all('td')[0].find('font').text).split(':')[0]
        port = (line[2*i].find_all('td')[0].find('font').text).split(':')[1]
        proxylist.append([address + ':' + port, get_time()])
        insert(proxylist)


#selenium
#...парсинг сайта https://advanced.name/ru/freeproxy
#переход по четырем страницам
def parsing_proxy4():
    print(get_time())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # открытие без графического интерфейса
    browser = webdriver.Chrome(options=options)
    browser.get('https://advanced.name/ru/freeproxy')
    soup1 = BeautifulSoup(browser.page_source, 'lxml')
    number_of_pages = len(soup1.find('body').find_all('section')[1].find("ul", class_="pagination pagination-lg").find_all('li'))-2
    for i in range(0,number_of_pages - 1):
        button = browser.find_element_by_id('pricing').find_element_by_class_name("pagination.pagination-lg").find_elements_by_tag_name('li')[number_of_pages+1].find_element_by_tag_name('a')
        button.click()
        time.sleep(10)
        soup = BeautifulSoup(browser.page_source, 'lxml')
        line = soup.find('body').find_all('section')[1].find("div", class_="table-responsive").find('table').find('tbody').find_all('tr')
        for tr in line:
            proxylist = list()
            address = tr.find_all('td')[1].text
            port = tr.find_all('td')[2].text
            proxylist.append([address + ':' + port, get_time()])
            insert(proxylist)



#парсинг сайта https://www.proxynova.com/proxy-server-list/
def parsing_proxy5():
    print('start')
    session = requests_html.HTMLSession()
    r = session.get('https://www.proxynova.com/proxy-server-list/')
    r.html.render(timeout=20) # timeout=20 базово стоит 8, перестало хватать
    for i in range(1, 21):
        proxylist = list()
        try:
            address = r.html.xpath('/html/body/div[3]/div[2]/table/tbody[1]/tr[{}]/td[1]/abbr/text()'.format(i))[1].replace(' ', '').replace('\n','')
            port = r.html.xpath('/html/body/div[3]/div[2]/table/tbody[1]/tr[{}]/td[2]/text()'.format(i))[0].replace(' ', '').replace('\n','')
            proxylist.append([address + ':' + port,get_time()])
            insert(proxylist)
        except Exception:
            pass




#проверяет отдельно взятую прокси
#обращение к сайту
def proxychecker(proxy):
    for site in ['http://www.google.com']:#,'https://yandex.ru','https://www.facebook.com'
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

#текущее время в минутах
def get_time():
    current_datetime = datetime.now()
    time_value = (((((current_datetime.year *12)+current_datetime.month)*30 + current_datetime.day)*24) + current_datetime.hour) *60 +current_datetime.minute
    return time_value
