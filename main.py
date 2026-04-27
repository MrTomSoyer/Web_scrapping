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
        return False


def search_in_post(driver, link_, keywords):
    main_window = driver.current_window_handle

    try:
        driver.execute_script('window.open(arguments[0]);', link_)
        driver.switch_to.window(driver.window_handles[-1])

        wait = WebDriverWait(driver, 10)
        body = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.article-body')
                or (By.ID, 'post-content-body')
            )
        )

        text = body.text.lower()
        result = any(word.lower() in text for word in keywords)
        return result

    except TimeoutException:
        print('Таймаут при загрузке страницы с постом')
        return False
    except NoSuchElementException:
        print('Не найден элемент страницы')
        return False
    except WebDriverException as e:
        print(f'Ошибка WebDriver: {e}')
        return False
    finally:
        if driver.current_window_handle != main_window:
            driver.close()
            driver.switch_to.window(main_window)


def safe_find(parent, by, selector):
    try:
        return parent.find_element(by, selector)
    except NoSuchElementException:
        return None


def safe_find_all(parent, by, selector):
    try:
        return parent.find_elements(by, selector)
    except NoSuchElementException:
        return []


def search_by_preview(keywords, is_search_in_post=False):
    driver = setup_driver()
    if not driver:
        return

    try:
        driver.get('https://habr.com/ru/articles')

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'article')
            or (By.CSS_SELECTOR, '.tm-articles-list__item')
        ))

        articles = (safe_find_all(driver, By.CSS_SELECTOR, 'article')
                    or safe_find_all(driver, By.CSS_SELECTOR, '.tm-articles-list__item')
                    )

        articles_data = []
        for article in articles:
            date_tag = safe_find(article, By.CSS_SELECTOR, 'time')
            date = date_tag.get_attribute('datetime')[:10] if date_tag else 'Дата не найдена'

            header_tag =(
                safe_find(article, By.CSS_SELECTOR, 'h2')
                or safe_find(article, By.CSS_SELECTOR, '.tm-title.tm-title_h2')
            )

            title = header_tag.text.strip().lower() if header_tag else 'Заголовок не найден'
            link_tag = (
                    safe_find(header_tag, By.CSS_SELECTOR, 'a' )
                    or safe_find(header_tag, By.CSS_SELECTOR, '.tm-articles-list__item')
            )
            link = link_tag.get_attribute('href') if link_tag else 'Ссылка не найдена'

            descriptions = (
                safe_find_all(article, By.CSS_SELECTOR, '.article-formatted-body')
                or safe_find_all(article, By.CSS_SELECTOR, '.lead')
            )
            content = '\n'.join([desc.text for desc in descriptions]).lower()

            articles_data.append({
                'data': date,
                'title': title,
                'link': link,
                'content': content
            })

        for article_data in articles_data:
            all_text = article_data['title'] + '\n' + article_data['content']
            found_in_preview = any(word.lower() in all_text for word in keywords)

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
