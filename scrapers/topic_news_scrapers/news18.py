import requests
from bs4 import BeautifulSoup

# URL of the website (Replace with the actual URL)
url = "https://www.news18.com/topics"

def news18_topic_scraper(url: str, topics: list, max_articles: int = 10):

    headers = {"User-Agent": "Mozilla/5.0"}

    links = []
    for topic in topics:
        topic = topic.replace(" ", "-").lower()
        url = f"{url}/{topic}/"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        list_items = soup.find_all("li", class_="jsx-894ab2deeb1b9f4a")
        topic_links = [item.find("a")["href"] if item.find("a") else "No link" for item in list_items]

        topic_links = topic_links[:min(max_articles, len(topic_links))]
        links.append((topic_links, topic))

    news = []
    for topic_links, topic in links:
        for link in topic_links:
            response = requests.get(link)

            soup = BeautifulSoup(response.content, 'html.parser')

            h2_tag = soup.find('h2', id=lambda x: x and x.startswith('asubttl'))
            h2_text = h2_tag.get_text() if h2_tag else 'No <h2> tag found'

            story_paras = soup.find_all('p', class_=lambda x: x and x.startswith('story_para_'))
            story_texts = [para.get_text() for para in story_paras]
            article_text = ' '.join(story_texts)

            first_published = soup.find('ul', class_='fp')
            first_published_text = first_published.get_text(strip=True) if first_published else 'No First Published date found'

            news.append({'title': h2_text, 'date_time': first_published_text, 'content': article_text, 'topic': topic})

    return news
