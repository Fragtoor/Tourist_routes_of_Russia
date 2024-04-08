from bs4 import BeautifulSoup as BS
import requests
BASE_URL = 'https://rg.ru/tema/ekonomika/turizm/'
URL_NEWS = 'https://rg.ru/'


def get_news(count=6):
    response = requests.get(BASE_URL)
    soup = BS(response.content, 'lxml')
    news = soup.find_all('div', class_='PageRubricContent_listItem__rjCcF')
    answer = []
    for new in news:
        url = URL_NEWS + new.find('a').get('href')
        time = new.find('a', class_='ItemOfListStandard_datetime__1tmwG').text
        text_new = new.find('span', class_='ItemOfListStandard_title__eX0Jw').text
        answer.append({'text': text_new, 'time': time, 'url': url})
    if 0 < count <= len(answer):
        answer = answer[:count]
    else:
        answer = answer[:6]
    return answer
