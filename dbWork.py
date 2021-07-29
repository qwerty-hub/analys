import sqlite3
from datetime import datetime


#...создание базы данных Sqlite
#хранит 2 таблицы: актуальные и умершие прокси
def createDb():
    connection = sqlite3.connect('proxy.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ProxyList
                    (proxy TEXT UNIQUE, Available TEXT DEFAULT('NONE'), GET INTEGER, checkk INTEGER, died INteger)''')
    connection.commit()

    cursor.execute('''CREATE TABLE IF NOT EXISTS DiedProxyList
                      (proxy TEXT UNIQUE, Available TEXT DEFAULT('NONE'), GET INTEGER, checkk INTEGER, Died INTEGER)''')
    connection.commit()

    connection.close()




#...вывод существующей базы данны
def printDb():
    connection = sqlite3.connect('proxy.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ProxyList")
    print('|.......proxy.......|...Available...|')
    for elem in cursor.fetchall():
        print(elem[0], '   ', elem[1])
    connection.commit()
    connection.close()


#вставка списка прокси в базу данных
def insert(proxylist):
    with sqlite3.connect('proxy.db') as connection:
        cursor = connection.cursor()
        try:
            cursor.executemany("INSERT INTO ProxyList (proxy, get) VALUES (?, ?)", proxylist)
            connection.commit()
        except Exception as e:
            #pass
            print(e)



# вставка списка умерших прокси в базу данных умерших прокси
#удаление умерших из актуального списка
def died_proxy():
        with sqlite3.connect('proxy.db') as connection:
            try:
                cursor = connection.cursor()
                list = cursor.execute("SELECT * FROM ProxyList WHERE Available = 'NO'")
                connection.commit()
                cursor.executemany("INSERT INTO DiedProxyList (proxy, Available, Get, Died) VALUES (?, ?, ?, ?)", list)
                connection.commit()
                cursor.executemany("DELETE FROM ProxyList WHERE Available = 'NO'")
                connection.commit()
            except Exception as e:
                pass

#среднее время жизни прокси
#не учитываем не работающие изначально
def died_proxyCheck():
    with sqlite3.connect('proxy.db') as connection:
        cursor = connection.cursor()
        records = cursor.execute("SELECT * FROM DiedProxyList")
        list= cursor.fetchall()
        count = 0
        value = 0
        for elem in list:
            if (elem[3] !=elem[4]):
                value = value + elem[4] - elem[3]
                count = count +1
        print('среднее время жизни в минутах: ', value/count)

#текущее время в минутах
def get_time():
    current_datetime = datetime.now()
    time_value = (((((current_datetime.year *12)+current_datetime.month)*30 + current_datetime.day)*24) + current_datetime.hour) *60 +current_datetime.minute
    return time_value




