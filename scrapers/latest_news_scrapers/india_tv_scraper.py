import requests
from bs4 import BeautifulSoup

URL = "https://www.indiatvnews.com/latest-news"
def india_tv_news_scraper(url: str = URL, max_articles: int = 10) -> list:    
    response = requests.get(url)

    if response.status_code == 200:
        news = []
        soup = BeautifulSoup(response.text, "html.parser")
        columns = soup.find_all("div", class_="box")
        for column in columns[:-4]:
            links = [a['href'] for a in column.find_all("a", href=True)]
            label_h2 = column.find("h2")
            label = None
            if label_h2:
                label = label_h2.get_text(strip=True)

            links = list(set(links))
            links = links[:min(max_articles, len(links))]
            for link in links:
                try:
                    link_response = requests.get(link, timeout=6)
                    if link_response.status_code == 200:
                        link_soup = BeautifulSoup(link_response.text, "html.parser")
                        headline = link_soup.find("h1", class_="arttitle")
                        title = headline.text
                        date_time = link_soup.find("time")
                        if date_time:
                            date_time = date_time["datetime"]
                        else:
                            date_time = None
                        content_div = link_soup.find("div", class_="content", id = "content")
                        full_content = None
                        if content_div:
                            paragraphs = content_div.find_all("p")
                            full_content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                        news.append({"title": title, "date_time": date_time, "content": full_content, "label":label})
                    else:
                        print(f"Failed to retrieve page, status code: {response.status_code}")
                        continue
                except requests.exceptions.Timeout:
                    print(f"Timeout error for link {link}")
                    continue
        print("Scraping complete. Total articles:", len(news))
        return news
    else:
        print(f"Failed to retrieve page, status code: {response.status_code}")