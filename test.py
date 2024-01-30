from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import random
import time

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

# Логин и пароль
USERNAME = open("userdata.txt").readlines()[0]
PASSWORD = open("userdata.txt").readlines()[1]

# Тест авторизации с верными данными
def test_Login():
   driver = webdriver.Chrome(options=options)
   driver.get("https://www.drive2.ru/")

   # Найти и нажать кнопку Войти
   driver.find_element(By.CSS_SELECTOR, '[data-testid="topbar.login"]').click()
   # Заполнить поля логин и пароль
   driver.find_element(By.NAME, "Login").send_keys(USERNAME)
   driver.find_element(By.NAME, "Password").send_keys(PASSWORD)

   # Нажать войти
   driver.find_element(By.CSS_SELECTOR, '[data-ym-target="login_from_reception_by_email"]').click()

   time.sleep(15) # Время на ввод капчи

   # При успешной авторизации появляется кнопка профиля, проверить наличие
   profile = driver.find_element(By.CSS_SELECTOR, '[data-ym-target="menu_myprofile"]')

   if profile != None:
      print("Авторизация прошла успешно.")

   assert profile != None

   return driver



# Тест открытия ленты новостей с верным фильтром
def test_ProperCarNews():
         
   driver = webdriver.Chrome(options=options)
   driver.get("https://www.drive2.ru/")

   # Нажать на кнопку Показать еще
   more_btn = driver.find_element(By.CSS_SELECTOR, '[data-action="filter.full"]')
   ActionChains(driver).move_to_element(more_btn).click(more_btn).perform()
   # Выбрать и запомнить выбранную марку авто
   car_list = driver.find_element(By.CSS_SELECTOR, '[data-slot="filter.root"]')
   car_list = car_list.find_elements(By.CLASS_NAME, 'c-index-makes__item.c-link.c-link--text')
   picked_car_num = random.randrange(len(car_list))
   picked_car = car_list[picked_car_num]
   picked_car_name = picked_car.text
   # Нажать на выбранную марку
   ActionChains(driver).move_to_element(picked_car).click(picked_car).perform()
   
   # Получить и сравнить результат с выбором
   opened_car_name = driver.find_element(By.CLASS_NAME, "x-title").text

   print('Выбранная страница: ' + picked_car_name + '\n' + 'Открывшаяся страница: ' + opened_car_name)

   assert opened_car_name == picked_car_name



# Заполнение только одного поля при регистрации
def test_InvalidRegData():

   driver = webdriver.Chrome(options=options)
   driver.get("https://www.drive2.ru/")
   # Найти и нажать на кнопку регистрации
   register = driver.find_element(By.CSS_SELECTOR, '[data-ym-target="menu_top_entry"]')
   ActionChains(driver).move_to_element(register).click(register).perform()
   # Заполнить поле Email
   driver.find_element(By.NAME, "Email").send_keys("bad email")
   # Нажать Зарегистрироваться
   driver.find_element(By.CSS_SELECTOR, '[data-app-target="registration:register_signup_confirm"]').click()
   # Проверить, появилась ли ошибка
   error = driver.find_element(By.CLASS_NAME, 'field-validation-error')

   if error != None:
      print(error.text)

   assert error != None



# Тест правильности фильтра по марке и модели
def test_NewsFilter():

   driver = test_Login()
   # Выбрать случайную марку из списка фильтра
   brand_select = Select(driver.find_element(By.CSS_SELECTOR, '[data-slot="carselect.brand"]'))

   brand_option_id = random.randrange(len(brand_select.options))
   brand_option_text = brand_select.options[brand_option_id].text

   brand_select.select_by_index(brand_option_id)

   time.sleep(2)
   # Выбрать случайную модель из списка фильтра
   model_select = Select(driver.find_element(By.CSS_SELECTOR, '[data-slot="carselect.model"]'))

   model_option_id = random.randrange(len(model_select.options))
   model_option_text = model_select.options[model_option_id].text

   model_select.select_by_index(model_option_id)

   time.sleep(2)
   # Запомнить выбранный фильтр
   picked_car_name = brand_option_text + ((' ' + model_option_text) if model_option_id != 0 else '')
   # Нажать Найти
   driver.find_element(By.CSS_SELECTOR, '[data-ym-target="exp_find"]').click()
   # Сравнить выбранный фильтр с рельультатом
   opened_car_name = driver.find_element(By.CLASS_NAME, "x-title").text

   print('Выбран фильтр: ' + picked_car_name + '\n' + 'Открывшаяся страница: ' + opened_car_name)
   assert picked_car_name == opened_car_name


# Тест поиска (наличие искомого слова в заголовках результатов)
def test_ProperSearch():

   driver = test_Login()

   search_text = "abc"
   # Найти строку поиска, ввести тексти и нажать Найти
   driver.find_element(By.NAME, "text").send_keys(search_text)
   driver.find_element(By.XPATH, "//button[contains(text(), 'Найти')]").click()

   time.sleep(2)
   # Получить заголовки всех статей в результатах
   article_headers = driver.find_element(By.CSS_SELECTOR, '[data-slot="site-search.results"]').find_elements(By.TAG_NAME, "h3")
   passed = True
   # Проверить, имеется ли в них поисковой запрос
   for header in article_headers:
      if search_text not in header.text.lower():
         print('В заголовке: ' + header.text + ' не найден текст ' + search_text) 
         passed = False

   if passed:
      print("Тест пройден успешно.")

   assert passed



# Подписка на автомобиль
def test_CarSubscribe():
   # Пройти авторизацию
   driver = test_Login()

   # Переменная-результат теста
   passed = False

   # Нажать на первый промо-автомобиль наверху страницы
   driver.find_element(By.CSS_SELECTOR, '[data-slot="promocars.link"]').click()
   # Сохранить название автомобиля
   car_name = driver.find_element(By.CLASS_NAME, 'x-title').text
   # Нажать Подписаться
   sub_btn = driver.find_element(By.CLASS_NAME, 'c-button.c-button--primary.c-button--l.is-big')
   ActionChains(driver).move_to_element(sub_btn).click(sub_btn).perform()

   
   # Перейти в профиль
   profile = driver.find_element(By.CSS_SELECTOR, '[data-ym-target="menu_myprofile"]')
   ActionChains(driver).move_to_element(profile).click(profile).perform()

   time.sleep(2)
   # Перейти в подписки
   driver.get("https://www.drive2.ru/users/blacksnow2402/carsfollowing")
   # Получить список подписок
   subscribes = driver.find_element(By.CLASS_NAME, 'o-grid.o-grid--2.o-grid--equal').find_elements(By.CLASS_NAME, 'c-darkening-hover-container')
   # Пройтись по подпискам, найти автомобиль, на который подписались
   for sub in subscribes:
      if car_name == sub.find_element(By.CLASS_NAME, 'c-car-title.c-link.c-link--current').text:
         passed = True

   assert passed



# Проверка совпадения предложения на Барахолке с Моим автомобилем
def test_ProperMarketRecommends():
   # Пройти авторизацию
   driver = test_Login()

   # Перейти в профиль
   driver.find_element(By.CSS_SELECTOR, '[data-ym-target="menu_myprofile"]').click()
   # Перейти на страницу автомобиля
   driver.find_element(By.CSS_SELECTOR, '[data-ym-target="user2car"]').click()
   # Записать марку и модель
   car_name = driver.find_element(By.CSS_SELECTOR, '[data-ym-target="car2gen"]').text
   # Перейти в Барахолку
   driver.find_element(By.CSS_SELECTOR, '[data-ym-target="menu_market"]').click()

   # Сравнить авто на барахолке с моим авто
   market_car_name = driver.find_element(By.CSS_SELECTOR, '[data-slot="market.block"]').find_element(By.TAG_NAME, 'h3').text

   print('Машина: ' + car_name + '. Машина на Барахолке: ' + market_car_name)

   assert car_name in market_car_name


# Проверка добавления закладки
def test_AddBookmark():
   # Пройти авторизацию
   driver = test_Login()
   
   # Переменная-результат теста
   passed = False

   # Сохранить заголовок первого поста
   post = driver.find_element(By.CLASS_NAME, 'c-post-share__title').find_element(By.TAG_NAME, 'a').text

   # Нажать на кнопку Добавить в закладки на первой записи
   add = driver.find_element(By.CSS_SELECTOR, '[data-tt="Добавить закладку"]')
   ActionChains(driver).move_to_element(add).click(add).perform()
   time.sleep(2) # ожидание всплывающего окна
   # Сохранить
   driver.find_element(By.CLASS_NAME, 'x-form__submit.u-extend.u-flow').find_element(By.NAME, 'submitbtn').click()

   # Перейти в Мои закладки
   driver.find_element(By.CSS_SELECTOR, '[data-ym-target="menu_my_bookmarks"]').click()

   bookmark_headers = driver.find_element(By.CSS_SELECTOR, '[data-slot="bookmarks.content"]').find_elements(By.TAG_NAME, 'h3')

   for header in bookmark_headers:
      if header.text == post:
         print('Тест пройден.')
         passed = True

   assert passed


# Выход из аккаунта
def test_Logout():
   # Пройти авторизацию
   driver = test_Login()

   # Нажать Настройки
   settings = driver.find_element(By.CSS_SELECTOR, '[data-ym-target="menu_top_settings"]')
   ActionChains(driver).move_to_element(settings).click(settings).perform()
   # Нажать Выход
   driver.find_element(By.CSS_SELECTOR, '[data-slot="top-menu.dropdown"]').find_element(By.XPATH, "//button[contains(text(), 'Выход')]").click()

   # Проверка появления кнопки Войти
   login_btn = driver.find_element(By.CSS_SELECTOR, '[data-testid="topbar.login"]')

   if login_btn != None:
      print('Выход произведен успешно')

   assert login_btn != None



def test_OpenVKPage():

   driver = webdriver.Chrome(options=options)
   driver.get("https://www.drive2.ru/")

   # Найти и нажать на кнопку ВКонтакте
   vk_btn = driver.find_element(By.CSS_SELECTOR, '[data-testid="footer-links.vk"]')
   ActionChains(driver).move_to_element(vk_btn).click(vk_btn).perform()

   # Переключиться на открытое окно
   driver.switch_to.window(driver.window_handles[1])

   # Проверить адрес открытой страницы
   if driver.current_url == 'https://vk.com/drive2':
      print('Открыта нужная страница')

   assert driver.current_url == 'https://vk.com/drive2'






#test_Login()
#test_ProperCarNews()
#test_InvalidRegData()
#test_NewsFilter()
#test_ProperSearch()
#test_CarSubscribe()
#test_ProperMarketRecommends()
#test_AddBookmark()
#test_Logout()
#test_OpenVKPage()