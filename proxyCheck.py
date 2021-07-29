import sqlite3
import urllib.request
from dbWork import get_time


#...проверяет все прокси из бд, результат записывает в бд
def proxyCheck():
    with sqlite3.connect('proxy.db') as connection:
        cursor = connection.cursor()
        records = cursor.execute("SELECT * FROM ProxyList")
        list= cursor.fetchall()
        for elem in list:
            if proxychecker(elem[0]):
                cursor.execute("""Update ProxyList set Available = 'YES', checkk = ?  where proxy = ?""",
                               (get_time(), elem[0]))
            else:
                cursor.execute("""Update ProxyList set Available = 'NO', checkk = ?, died = ? where proxy = ?""",
                               (get_time(), get_time(), elem[0],))
            connection.commit()

#...проверяет новые прокси из бд
def checkNewProxy():
    with sqlite3.connect('proxy.db') as connection:
        cursor = connection.cursor()
        records = cursor.execute("SELECT * FROM ProxyList  WHERE Available = 'NONE'")
        list= cursor.fetchall()
        for elem in list:
            if proxychecker(elem[0]):
                cursor.execute("""Update ProxyList set Available = 'YES', checkk = ?  where proxy = ?""", (get_time(), elem[0]))
            else:
                cursor.execute("""Update ProxyList set Available = 'NO', checkk = ?, died = ? where proxy = ?""", (get_time(), get_time(), elem[0],))
            connection.commit()

#...проверяет новые прокси из бд
#выводит статистику
def checkNewProxy_info(name):
    file = open("info.txt", "w")
    print('Время начала проверки', get_time())
    file.write(name)
    file.write('Время начала проверки' + str(get_time()) + '\n')
    with sqlite3.connect('proxy.db') as connection:
        cursor = connection.cursor()
        records = cursor.execute("SELECT * FROM ProxyList  WHERE Available = 'NONE'")
        list= cursor.fetchall()
        good = 0
        bad = 0
        for elem in list:
            if proxychecker(elem[0]):
                cursor.execute("""Update ProxyList set Available = 'YES', checkk = ?  where proxy = ?""", (get_time(), elem[0]))
                good =good + 1
            else:
                cursor.execute("""Update ProxyList set Available = 'NO', checkk = ?, died = ? where proxy = ?""", (get_time(), get_time(), elem[0],))
                bad =bad +1
            print('good: ' , good , ' bad: ' , bad , 'toatal: ', good + bad, ' profit: ', good / (good + bad) * 100, '% ')
            file.write('good: '+ str(good) + ' bad: ' + str(bad) + 'toatal: ' + str(good + bad) + ' profit: ' + str(int(good/(good + bad)*100)) + '% \n' )
            connection.commit()
    print('Время окончания проверки:', get_time())
    file.write('Время окончания проверки:' + str(get_time()))
    file.close()

#...проверяет работающие прокси в бд
def checkOldProxy():
    with sqlite3.connect('proxy.db') as connection:
        cursor = connection.cursor()
        records = cursor.execute("SELECT * FROM ProxyList  WHERE Available = 'YES'")
        list= cursor.fetchall()
        for elem in list:
            if not(proxychecker(elem[0])):
                cursor.execute("""Update ProxyList set Available = 'NO', died = ? where proxy = ?""", (get_time(), elem[0],))
            connection.commit()



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


