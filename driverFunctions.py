import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from twocaptcha import TwoCaptcha
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
import chromedriver_binary 
import urllib
import urllib.request
import time

api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR-API-KEY')
solver = TwoCaptcha(api_key)

def page_opening(driver):
  try:
    WebDriverWait(driver, 3).until(lambda x: x.find_element_by_css_selector('.AdvancedCaptcha-Image'))
  except Exception as e:
    print('No Captcha-Image, opening page...')
    try:
      WebDriverWait(driver, 120).until(lambda x: x.find_element_by_css_selector('.main'))
    except Exception as e:
      driver.quit()
      return 0
    else:
      requiredHtml = driver.page_source
      return requiredHtml
  else:
    print('Found Captcha-Image')
    image = driver.find_element_by_css_selector('.AdvancedCaptcha-Image')
    src = image.get_attribute('src')
    urllib.request.urlretrieve(src, "images/captcha.png")

    try:
      result = solver.normal('images/captcha.png')
    except Exception as e:
      driver.quit()
      return 0
    else: 
      print('received solving: ' + str(result['code']) + ' id: ' +  str(result['captchaId']))
      driver.find_element_by_css_selector('.Textinput-Control').send_keys(result['code'])
      driver.find_element_by_css_selector('button[type=submit]').click()

      try:
        WebDriverWait(driver, 1).until(lambda x: x.find_element_by_css_selector(".Textinput-Hint"))
      except Exception as e:
        print('solving success')
        # solver.report(result['captchaId'], True)
      else:
        print('solving incorrect')
        # solver.report(result['captchaId'], False)
        driver.quit()
        return 0

    try:
      WebDriverWait(driver, 60).until(lambda x: x.find_element_by_css_selector('.main'))
    except Exception as e:
      driver.quit()
      return 0
    else:
      requiredHtml = driver.page_source
      return requiredHtml

def go_page(link):
  print('Getting page ' + link + '...')
  
  chrome_options = Options()
  driver = webdriver.Chrome()
  driver.get(link)

  try:
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_css_selector('.CheckboxCaptcha-Button'))
  except Exception as e:
    print('No CheckboxCaptcha-Button')
    result = page_opening(driver)
    return result
  else:
    print('Found CheckboxCaptcha-Button')
    driver.find_element_by_css_selector('.CheckboxCaptcha-Button').click()
    result = page_opening(driver)
    return result