# parser-v2-public  
Yandex market parser  
Парсинг отзывов на товары с яндекс маркета (отзывы >= 3 звезд ), запись информации в xlsx (товар, автор, количество звезд, достоинства, недостатки, отзыв, ссылки на фото, дата).  
  
Python 3.9  
cmd команды в папке проекта  
Создание среды: python -m venv env  
Активация среды: path\env\Scripts\activate  
Установка пакетов: pip install beautifulsoup4 requests lxml selenium 2captcha-python chromedriver-binary pandas openpyxl  
Запуск: python pars-product.py  
  
Подключен сервис rucaptcha для решения капч. Вставить ключ вместо 'YOUR-API-KEY'.  
Если используется другой сервис, изменить в driverFunctions.  
Не использовать сервис: в driverFunctions убрать вызов solver, вводить капчи вручную.
