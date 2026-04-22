from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.page_load_strategy = 'eager'
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        print(f"Ошибка WebDriver: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        return False


def search_in_post(driver, link_, word):
    try:
        driver.get(link_)
        wait = WebDriverWait(driver, 10)
        text_box = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                'div[xmlns="http://www.w3.org/1999/xhtml"]'
            ))
        )
        return word in text_box.text.lower()

    except TimeoutException:
        print("Таймаут при загрузке страницы с постом")
        return False
    except NoSuchElementException:
        print('Не найден элемент страницы')
        return False
    except WebDriverException as e:
        print(f"Ошибка инициализации WebDriver: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        return False


def search_by_preview(keywords, is_search_in_post=False):
    driver = setup_driver()
    if not driver:
        return

    try:
        driver.get("https://habr.com/ru/articles")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))
        articles = driver.find_elements(by=By.TAG_NAME, value="article")

        articles_data = []
        for element in articles:
            if not element.is_displayed():
                continue

            time_tag = element.find_element(by=By.TAG_NAME, value="time")
            data = time_tag.get_attribute("datetime")[:10]

            header_tag = element.find_element(By.TAG_NAME, "h2")
            title = header_tag.text

            link_tag = header_tag.find_element(By.TAG_NAME, "a")
            link = link_tag.get_attribute("href")

            descriptions = element.find_elements(By.TAG_NAME, "p")
            content = '\n'.join([desc.text for desc in descriptions])

            articles_data.append({
                'data': data,
                'title': title,
                'link': link,
                'content': content.lower()
            })

        for article_data in articles_data:
            all_text = article_data['title'].lower() + '\n' + article_data['content']

            for word in keywords:
                if word in all_text:
                    print(f'{article_data['data']}\n{article_data['title']}\n{article_data['link']}\n-----')
                    break
                elif is_search_in_post and search_in_post(driver, article_data['link'], word):
                    print(f'{article_data['data']}\n{article_data['title']}\n{article_data['link']}\n-----')
                    break

    except TimeoutException:
        print("Таймаут при загрузке страницы с превью")
    except WebDriverException as e:
        print(f"Ошибка WebDriver: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
    finally:
        if driver:
            driver.quit()

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

if __name__ == "__main__":
    search_by_preview(KEYWORDS)
    # # Поиск внутри статьи
    # search_by_preview(KEYWORDS, True)
