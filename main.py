from parser1 import parsing_proxy1
from parser1 import parsing_proxy2
from parser1 import parsing_proxy3
from parser1 import parsing_proxy4
from parser1 import parsing_proxy5
from parser1 import get_time
from proxyCheck import checkNewProxy_info
from dbWork import createDb


#   существует 5 функций парсинга 5ти сайтов, каждая функция записывает прокси в бд proxy в таблицу ProxyList
#   для каждой новой прокси присвает атрибуту Available значение NONE(проверка прокси не производится)
#   функция checkNewProxy производит проверку всех новых прокси(атрибут Available имеет значение NONE)
#   проверка производится путем подключения к списку сайтов (сейчас 3)
#   по результатам проверки атрибут Available будет иметь значение YES или NO (прокси работает или нет)
#   Так же у каждой прокси в атрибуте CHECKK будет время ее первой проверки в минутах
#   Аналогично реализована функция проверки старых работающих прокси checkOldProxy
#   Когда программа обнаружит что прокси перестала работать в атрибуте DIED будет находиться время когда это было замечено
#   функция died_proxy перемещает все неработающие прокси из таблицы ProxyList в таблицу DiedProxyList
#   для последующего анализа среднего времени жизни прокси
#


#   атрибут CHECKK, а не CHECK  тк иначе возникает ошибка в запросе
#   checkNewProxy_Info выполняет проверку новых прокси и выводит: время начала и окончания проверки,
#   текущее количество плохих, хороших  и процент хороших
#   информация выводится на экран и в файл info



createDb()

print(get_time())
parsing_proxy1()
print(get_time())
checkNewProxy_info('https://free-proxy-list.net/')

print(get_time())
parsing_proxy2()
print(get_time())
checkNewProxy_info('http://foxtools.ru/')

print(get_time())
parsing_proxy3()
print(get_time())
checkNewProxy_info('https://spys.one/en/free-proxy-list/')

print(get_time())
parsing_proxy4()
print(get_time())
checkNewProxy_info('https://advanced.name/ru/freeproxy')

print(get_time())
parsing_proxy5()
print(get_time())
checkNewProxy_info('https://www.proxynova.com/proxy-server-list/')