import os
import math
from bs4 import BeautifulSoup
import pandas as pd
import driverFunctions

class ParsCategoryPage:
    def __init__(self):
        self.productList = []
        self.DIR = ''
        self.CATEGORY = ''
        self.URL = ''
        self.page = 0

    def pars_page(self, soup):
      if self.page == 2:          # stop after 2 searched pages. comment this condition if need to search ALL pages in category
        return
      _list = soup.find("div", {"data-apiary-widget-name": "@MarketNode/SearchResults"})
      articles = _list.find_all('article')
      for article in articles:    # search if product has reviews
          if article.find("a", {"data-zone-name": "rating"}):
              h3 = article.find('h3')
              name = (h3.find('span')).text
              href = 'https://market.yandex.ru' + h3.find('a')['href']
              span = (article.find("a", {"data-zone-name": "rating"})).find_all('span')[1]
              revs = (span.text).split(' ')[0] 
              self.productList.append([name, href, revs])     # add info to array: name of product, link to product, reviews quantity
          else:                   # if product hasn't reviews, skip it
              continue

      if (soup.find("div", {"data-apiary-widget-name": "@MarketNode/SearchPager"})):
          searchPager = soup.find("div", {"data-apiary-widget-name": "@MarketNode/SearchPager"})
          if ("Показать ещё" in searchPager.text):
              nextPage = searchPager.find('a', {'aria-label': 'Следующая страница'})
              link = 'https://market.yandex.ru' + nextPage['href']
              print('Next page: ' + link)

              pageIndex = link.split('&page=')[1]
              print('pageIndex: ' + pageIndex)
              file = self.DIR + '/' + self.CATEGORY + pageIndex + '.html'
              if not os.path.exists(file):
                  pageHtml = driverFunctions.go_page(link)
                  if pageHtml == 0:
                      while pageHtml == 0:
                          pageHtml = driverFunctions.go_page(link)
                  with open(self.DIR + '/' + self.CATEGORY + pageIndex + '.html', 'w', encoding="utf-8") as file:
                      file.write(pageHtml)
              else:
                  with open (file, encoding="utf8") as file:
                      pageHtml = file.read()

              soup = BeautifulSoup(pageHtml, "lxml") # parser init
              self.page += 1
              self.pars_page(soup)
          else:
              return

    def getProductList(self):
        if not os.path.exists(self.DIR):
            os.mkdir(self.DIR)  # create folder with category name
            categoryHtml = driverFunctions.go_page(self.URL)
            if categoryHtml == 0:
                while categoryHtml == 0:
                    categoryHtml = driverFunctions.go_page(self.URL)
            with open(self.DIR + '/' + self.CATEGORY + '.html', 'w', encoding="utf-8") as file:
                file.write(categoryHtml)
        else:
            with open (self.DIR + '/' + self.CATEGORY + '.html', encoding="utf8") as file:
                categoryHtml = file.read()

        soup = BeautifulSoup(categoryHtml, "lxml") # parser init

        self.pars_page(soup)

        print('Found ' + str(len(self.productList)) + ' products with reviews')
        return self.productList

    
