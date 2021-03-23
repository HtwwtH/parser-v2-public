import os
import math
from bs4 import BeautifulSoup
import pandas as pd
from ParsCategory import ParsCategoryPage 
import driverFunctions

data = [
{"URL": "https://market.yandex.ru/catalog--sukhie-korma-v-krasnoiarske/75265/list?cpa=0&hid=15685787&how=opinions&glfilter=7893318%3A12686325%2C16806371%2C12686341&glfilter=13333460%3A13333461&onstock=1&local-offers-first=0&viewtype=list",
"CATEGORY": "Dog food"},
{"URL": "https://market.yandex.ru/catalog--sumki-chekhly-dlia-foto-i-videotekhniki-v-krasnoiarske/18041951/list?cpa=0&hid=90616&onstock=1&how=opinions&local-offers-first=0",
"CATEGORY": "Сумки, кейсы, чехлы"}
]

class reviewData:
  def __init__(self):
    self.product = []
    self.author_name = []
    self.rating = []
    self.advantages = []
    self.disadvantages = []
    self.review = []
    self.photos = []
    self.date = []

  def add_product(self, product):
    self.product.append(product)

  def add_author_name(self, author_name):
    self.author_name.append(author_name)

  def add_rating(self, rating):
    self.rating.append(rating)

  def add_advantages(self, advantages):
    self.advantages.append(advantages)

  def add_disadvantages(self, disadvantages):
    self.disadvantages.append(disadvantages)

  def add_review(self, review):
    self.review.append(review)

  def add_photos(self, photos):
    self.photos.append(photos)

  def add_date(self, date):
    self.date.append(date)
  
  def get_dataframe(self):
    # print(len(self.product), len(self.author_name), len(self.rating), len(self.advantages), len(self.disadvantages), len(self.review), len(self.photos), len(self.date))
    df = pd.DataFrame({
                   'Товар': self.product,
                   'Имя автора отзыва': self.author_name,
                   'Количество звезд': self.rating,
                   'Достоинства': self.advantages,
                   'Недостатки': self.disadvantages,
                   'Тело комментария': self.review,
                   'Фотографии': self.photos,
                   'Дата отзыва': self.date
                   })
    return df

  def clear_all(self):
    self.product = []
    self.author_name = []
    self.rating = []
    self.advantages = []
    self.disadvantages = []
    self.review = []
    self.photos = []
    self.date = []

def create_directories():             # create main directories if not exist
  if not os.path.exists('CATEGORIES'):
    os.mkdir('CATEGORIES') 
  if not os.path.exists('REPORTS'):
    os.mkdir('REPORTS') 
  if not os.path.exists('images'):
    os.mkdir('images') 
  return

def correct_name(name):
  if "/" in name:
    name = name.replace("/", "-")
  if '"' in name:
    name = name.replace('"', '')
  if "*" in name:
    name = name.replace("*", "")
  if ":" in name:
    name = name.replace(":", "-")
  return name

def find_product_name(soup):
  h1 = soup.find('h1')
  name = h1.text
  print("H1 product name: " + name)
  return name

def find_review_href(soup):
  hrefs = soup.find_all('a')
  for item in hrefs:
    text = item.get_text(strip=True) if item else ''
    if ('Отзывы' in text):
      spans = item.find_all('span')
      if (len(spans) == 2):
        print(spans[1].text)
        reviewsCount = spans[1].text
      review_tag = item
      # print(review_tag['href'])
      href = review_tag['href']
      print('in find_review_href')
      print('href: ' + href)
      print('reviewsCount: ' + reviewsCount)
      return [href, reviewsCount]

def get_review_author_name(review):
  if ("Имя скрыто" in review.text):
      return 'Имя скрыто'
  if ("Пользователь удален" in review.text):
      return 'Пользователь удален'
  else:
    tag = review.find("div", {"data-zone-name": "name"})
    href = tag.find('a')
    author_name = (href.find('div')).text + ' market.yandex.ru' + href['href']
    return author_name


def get_review_rating(review):
  div = review.find('div', {"class": "autotest-RatingStars"})
  puncts = div.find_all('i')
  for punct in puncts:
    if (punct.find('path', {"class": "_2-MzwPkbZd"})):
      grayStar = punct.find('path', {"class": "_2-MzwPkbZd"})
      rating = int(punct['data-rate']) - 1
      return rating
  return 5

def get_review_advantages(review):
  dls = review.find_all('dl')
  for dl in dls:
    if dl.find('dt'):
      if ('Достоинства:' in dl.find('dt').text):
        advantages = dl.find('dd').text
        return advantages
  return '-'

def get_review_disadvantages(review):
  dls = review.find_all('dl')
  for dl in dls:
    if dl.find('dt'):
      if ('Недостатки:' in dl.find('dt').text):
        disadvantages = dl.find('dd').text
        return disadvantages
  return '-'

def get_review_body(review):
  dls = review.find_all('dl')
  for dl in dls:
    if dl.find('dt'):
      if ('Комментарий:' in dl.find('dt').text):
        review_body = dl.find('dd').text
        return review_body
  if (len(dls) == 1 and dl.find('dd').text):
    review_body = dl.find('dd').text
    return review_body
  return '-'

def get_review_photos(review):
  tag = review.find("div", {"data-zone-name": "product-review-photos"})
  if tag:
    imgs = tag.find_all('img')
    imgList = ""
    if imgs:
      for img in imgs:
        imgList += img['src'] + "\r\n"
      return imgList
  return '-'

def get_review_date(review):
  buttons = review.find_all('button')
  for btn in buttons:
    if btn.text == 'Комментировать':
      span = btn.parent
      date = (span.next_sibling).text
      return date

def pars_review(product, soup, name):
  reviewsList = soup.find("div", {"data-apiary-widget-name": "@MarketNode/ProductReviewsList"})
  reviewsToolbar = soup.find("div", {"data-apiary-widget-name": "@MarketNode/ReviewsToolbar"})
  reviewsToolbarText = reviewsToolbar.get_text(strip=True) if reviewsToolbar else ''
  if (not reviewsList or ("Отзывов с текстом ещё нет" in reviewsToolbarText)):  #не рассматриваются случаи, когда нет отзывов вообще либо нет текстовых отзывов
    print("no reviews")
    product.add_product(name)       # добавить имя в поле класса
    product.add_author_name('-')
    product.add_rating('-')
    product.add_advantages('-')
    product.add_disadvantages('-')
    product.add_review('-')
    product.add_photos('-')
    product.add_date('-')
    product.get_dataframe()
  else:
    print("searching for reviews...")
    reviews = reviewsList.find_all("div", {"data-zone-name": "product-review"})
    for review in reviews:        # извлечение информации из отзыва
      rating = get_review_rating(review)
      # print('Rating: ' + str(rating))
      if (rating < 3):
        continue
      else:
        product.add_rating(rating)

      product.add_product(name)       

      author_name = get_review_author_name(review)
      # print('Author name: ' + author_name)
      product.add_author_name(author_name)

      advantages = get_review_advantages(review)
      # print('Advantages: ' + advantages)
      product.add_advantages(advantages)

      disadvantages = get_review_disadvantages(review)
      # print('Disadvantages: ' + disadvantages)
      product.add_disadvantages(disadvantages)
      
      review_body = get_review_body(review)
      # print('Review: ' + review_body)
      product.add_review(review_body)

      photos = get_review_photos(review)
      # print('Photos: ' + photos)
      product.add_photos(photos)

      date = get_review_date(review)
      # print('Date: ' + date)
      product.add_date(date)



# PROGRAM START
create_directories()

for cat in data:
  URL = cat['URL']
  CATEGORY = cat['CATEGORY']
  DIR = "CATEGORIES/" + cat['CATEGORY']

  product = reviewData()          # create class example with review functions
  parsingCategory = ParsCategoryPage()      # create class example with category parsing functions (from file ParsCategory)
  parsingCategory.DIR = DIR                 # set file path, for example CATEGORIES/dog food
  parsingCategory.CATEGORY = CATEGORY       # set category name
  parsingCategory.URL = URL                 # set link
  productList = parsingCategory.getProductList()  # get array of all found products with reviews: [{name: link}, ...]
  # print(productList)
  # exit()

  for item in productList:
    filename = item[0]
    link = item[1]
    reviewsCount = item[2]

    filename = correct_name(filename)

    print("Parsing of " + filename + ": " + link)

    file = DIR + "/products/" + filename + "/" + filename + ".html"
    if not os.path.exists(file):
      productHtml = driverFunctions.go_page(link)
      if productHtml == 0:
        while productHtml == 0:       # if returned 0 (some errors/unsuccess), try again
          productHtml = driverFunctions.go_page(link)
    else:
      with open (file, encoding="utf8") as file:
        productHtml = file.read()

    soup = BeautifulSoup(productHtml, "lxml") # parser init
    name = find_product_name(soup)  # search name from h1
    name = correct_name(name)

    if not os.path.exists(DIR + '/products/' + name):
      os.makedirs(DIR + '/products/' + name)  # create unique folder for product if not exist

    if not os.path.exists('REPORTS/' + CATEGORY + '/' + name):
      os.makedirs('REPORTS/' + CATEGORY + '/' + name)  # create unique folder for product report in xlsx

    filePath=''
    if not os.path.exists(DIR + '/products/' + name + '/' + name + '.html'):
      s = DIR + '/products/' + name + '/' + name + '.html'

      if len(s) + 33 >= 256:                          #cut too long names, they call error of file creating
        shortName = name.replace(" ", "")
        shortName = shortName[22:]
        with open(DIR + '/products/' + shortName + '/' + name + '.html', 'w', encoding="utf-8") as file:   # save html of product web page
          file.write(productHtml)
          filePath = DIR + '/products/' + shortName + '/' + name + '.html'
      else:
        with open(DIR + '/products/' + name + '/' + name + '.html', 'w', encoding="utf-8") as file:   # save html of product web page
          file.write(productHtml)
          filePath = DIR + '/products/' + name + '/' + name + '.html'
    else:
      filePath=DIR + '/products/' + name + '/' + name + '.html'
    
    with open (filePath, encoding="utf8") as file:      # read and parse html of product web page 
        src = file.read()

    soup = BeautifulSoup(src, "lxml") # parser init

    try:
      reviewHref, reviewsCount = find_review_href(soup) # find link to reviews page and quantity of reviews
    except Exception as e:                              # no link or some error - skip this product
      continue
    else:
      reviewHref = 'https://market.yandex.ru' + reviewHref;  # full link to reviews page

      print("Got href to review page: " + reviewHref)
      print("Reviews: " + str(reviewsCount))

      pagesCount = math.ceil(int(reviewsCount) / 10)    # how many pages of reviews (10 reviews per page)
      print("Pages: " + str(pagesCount))

      if not os.path.exists(DIR + "/products/" + name + "/review-page1.html"):
        review_html = driverFunctions.go_page(reviewHref)    # find and save html of first reviews page
        if review_html == 0:                        # some errors - try again
          while review_html == 0:
            review_html = driverFunctions.go_page(reviewHref)
        with open(DIR + '/products/' + name + '/review-page1.html', 'w', encoding="utf-8") as file:
          file.write(review_html)

      file=DIR + '/products/' + name + '/review-page1.html'
      with open (file, encoding="utf8") as file:
          src = file.read()

      reviewSoup = BeautifulSoup(src, "lxml") # parser init
      pars_review(product, reviewSoup, name)  # parse review page, push info to array

      if (reviewSoup.find('div'), {"data-apiary-widget-name": "@MarketNode/ProductReviewsPaginator"}):  #check that links to other reviews pages exist and create list of links mannually
        hrefs = []
        for i in range(1, pagesCount):
          hrefs.append(reviewHref + '&page=' + str(i+1))
        # print(hrefs)
        for count, href in enumerate(hrefs):
          pageIndex = count + 2
          print('Reviews page № ' + str(pageIndex))
          reviewHref = href
          print('Link to reviews page: ' + reviewHref)

          if not os.path.exists(DIR + '/products/' + name + '/review-page' + str(pageIndex) + '.html'):
            review_html = driverFunctions.go_page(reviewHref)
            if review_html == 0:
              while review_html == 0:
                review_html = driverFunctions.go_page(reviewHref)
            with open(DIR + '/products/' + name + '/review-page' + str(pageIndex) + '.html', 'w', encoding="utf-8") as file:
              file.write(review_html)

          file = DIR + '/products/' + name + '/review-page' + str(pageIndex) + '.html'
          with open (file, encoding="utf8") as file:
              src = file.read()
          
          reviewSoup = BeautifulSoup(src, "lxml") # parser init
          pars_review(product, reviewSoup, name)

      df = product.get_dataframe()
      file=''
      reportsFile = ''
      s = DIR + '/products/' + name + '/' + name + '.xlsx'
      if len(s) + 33 >= 256:
        shortName = name.replace(" ", "")
        shortName = shortName[22:]
        file = DIR + '/products/' + name + '/' + shortName + '.xlsx'
        reportsFile = 'REPORTS/' + CATEGORY + '/' + name + '/' + shortName + '.xlsx'
      else:
        file = DIR + '/products/' + name + '/' + name + '.xlsx'
        reportsFile = 'REPORTS/' + CATEGORY + '/' + name + '/' + name + '.xlsx'

      print('write to path: ' + file)
      if not os.path.exists(file):
        df.to_excel(file, sheet_name='Reviews', index=False)  # write xlsx report to CATEGORIES/product

      print('write to path: ' + reportsFile)
      if not os.path.exists(reportsFile):
        df.to_excel(reportsFile, sheet_name='Reviews', index=False)  # write xlsx report to REPORTS/product

      product.clear_all()

