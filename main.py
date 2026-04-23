from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.page_load_strategy = 'eager'
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        print(f'Ошибка WebDriver: {e}')
        print(f'Тип ошибки: {type(e).__name__}')
        return False


def search_in_post(driver, link_, keywords):
    main_window = driver.current_window_handle

    try:
        driver.execute_script("window.open(arguments[0]);", link_)
        driver.switch_to.window(driver.window_handles[-1])

        wait = WebDriverWait(driver, 10)
        text_box = wait.until(
            EC.presence_of_element_located((
                By.ID, 'post-content-body'
            ))
        )

        text = text_box.text.lower()
        result = any(word in text for word in keywords)

        return result

    except TimeoutException:
        print('Таймаут при загрузке страницы с постом')
        return False
    except NoSuchElementException:
        print('Не найден элемент страницы')
        return False
    except WebDriverException as e:
        print(f'Ошибка инициализации WebDriver: {e}')
        print(f'Тип ошибки: {type(e).__name__}')
        return False
    finally:
        if driver.current_window_handle != main_window:
            driver.close()
            driver.switch_to.window(main_window)


def search_by_preview(keywords, is_search_in_post=False):
    driver = setup_driver()
    if not driver:
        return

    try:
        driver.get('https://habr.com/ru/articles')
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article')))
        articles = driver.find_elements(By.CSS_SELECTOR, 'article')

        articles_data = []
        for element in articles:
            date_tag = element.find_element(By.CSS_SELECTOR, 'time')
            data = date_tag.get_attribute('datetime')[:10]

            header_tag = element.find_element(By.CSS_SELECTOR, 'a.tm-title__link')
            title = header_tag.text
            link = header_tag.get_attribute('href')

            descriptions = element.find_elements(By.CSS_SELECTOR,'.article-formatted-body')
            content = '\n'.join([desc.text for desc in descriptions])

            articles_data.append({
                'data': data,
                'title': title,
                'link': link,
                'content': content.lower()
            })

        for article_data in articles_data:
            all_text = article_data['title'].lower() + '\n' + article_data['content']
            found_in_preview = any(word in all_text for word in keywords)

            if found_in_preview:
                is_found = True
            elif is_search_in_post:
                is_found = search_in_post(driver, article_data['link'], keywords)
            else:
                is_found = False

            if is_found:
                print(f'<{article_data["data"]}> — <{article_data["title"]}> — <{article_data["link"]}>')

    except TimeoutException:
        print('Таймаут при загрузке страницы с превью')
    except WebDriverException as e:
        print(f'Ошибка WebDriver: {e}')
    except Exception as e:
        print(f'Ошибка: {e}')
        print(f'Тип ошибки: {type(e).__name__}')
    finally:
        if driver:
            driver.quit()

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

if __name__ == '__main__':
    #search_by_preview(KEYWORDS)
    # Поиск внутри статьи
    search_by_preview(KEYWORDS, True)
