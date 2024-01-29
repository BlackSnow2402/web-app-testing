from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import random
import time

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

USERNAME = open("userdata.txt").readlines()[0]
PASSWORD = open("userdata.txt").readlines()[1]

# Тест авторизации с верными данными
def test_Login():
   driver = webdriver.Chrome(options=options)
   driver.get("https://www.drive2.ru/")

   driver.find_element(By.CSS_SELECTOR, '[data-testid="topbar.login"]').click()
   driver.find_element(By.NAME, "Login").send_keys(USERNAME)
   driver.find_element(By.NAME, "Password").send_keys(PASSWORD)

   driver.find_element(By.CSS_SELECTOR, '[data-ym-target="login_from_reception_by_email"]').click()

   time.sleep(15) # Время на ввод капчи

   profile = driver.find_element(By.CSS_SELECTOR, '[data-ym-target="menu_myprofile"]')

   if profile != None:
      print("Авторизация прошла успешно.")

   assert profile != None

   return driver



# Тест открытия ленты новостей с верным фильтром
def test_ProperCarNews():
         
   driver = webdriver.Chrome(options=options)
   driver.get("https://www.drive2.ru/")

   more_btn = driver.find_element(By.CSS_SELECTOR, '[data-action="filter.full"]')
   ActionChains(driver).move_to_element(more_btn).click(more_btn).perform()

   car_list = driver.find_element(By.CSS_SELECTOR, '[data-slot="filter.root"]')
   car_list = car_list.find_elements(By.CLASS_NAME, 'c-index-makes__item.c-link.c-link--text')
   picked_car_num = random.randrange(len(car_list))
   picked_car = car_list[picked_car_num]
   picked_car_name = picked_car.text
   
   ActionChains(driver).move_to_element(picked_car).click(picked_car).perform()
   opened_car_name = driver.find_element(By.CLASS_NAME, "x-title").text

   print('Выбранная страница: ' + picked_car_name + '\n' + 'Открывшаяся страница: ' + opened_car_name)

   assert opened_car_name == picked_car_name



# Заполнение только одного поля при регистрации
def test_InvalidRegData():

   driver = webdriver.Chrome(options=options)
   driver.get("https://www.drive2.ru/")

   register = driver.find_element(By.CSS_SELECTOR, '[data-ym-target="menu_top_entry"]')
   ActionChains(driver).move_to_element(register).click(register).perform()
   driver.find_element(By.NAME, "Email").send_keys("bad email")
   driver.find_element(By.CSS_SELECTOR, '[data-app-target="registration:register_signup_confirm"]').click()
   error = driver.find_element(By.CLASS_NAME, 'field-validation-error')

   if error != None:
      print(error.text)

   assert error != None



# Тест правильности фильтра по марке и модели
def test_NewsFilter():

   driver = test_Login()

   brand_select = Select(driver.find_element(By.CSS_SELECTOR, '[data-slot="carselect.brand"]'))

   brand_option_id = random.randrange(len(brand_select.options))
   brand_option_text = brand_select.options[brand_option_id].text

   brand_select.select_by_index(brand_option_id)

   time.sleep(2)

   model_select = Select(driver.find_element(By.CSS_SELECTOR, '[data-slot="carselect.model"]'))

   model_option_id = random.randrange(len(model_select.options))
   model_option_text = model_select.options[model_option_id].text

   model_select.select_by_index(model_option_id)

   time.sleep(2)

   picked_car_name = brand_option_text + ((' ' + model_option_text) if model_option_id != 0 else '')

   driver.find_element(By.CSS_SELECTOR, '[data-ym-target="exp_find"]').click()

   opened_car_name = driver.find_element(By.CLASS_NAME, "x-title").text

   print('Выбран фильтр: ' + picked_car_name + '\n' + 'Открывшаяся страница: ' + opened_car_name)
   assert picked_car_name == opened_car_name


# Тест поиска (наличие искомого слова в заголовках результатов)
def test_ProperSearch():

   driver = test_Login()

   search_text = "abc"

   driver.find_element(By.NAME, "text").send_keys(search_text)
   driver.find_element(By.XPATH, "//button[contains(text(), 'Найти')]").click()

   time.sleep(2)

   article_headers = driver.find_element(By.CSS_SELECTOR, '[data-slot="site-search.results"]').find_elements(By.TAG_NAME, "h3")
   passed = True

   for header in article_headers:
      if search_text not in header.text.lower():
         print('В заголовке: ' + header.text + ' не найден текст ' + search_text) 
         passed = False

   if passed:
      print("Тест пройден успешно.")

   assert passed


   
#test_NewsFilter()
#test_Login()
#test_ProperSearch()