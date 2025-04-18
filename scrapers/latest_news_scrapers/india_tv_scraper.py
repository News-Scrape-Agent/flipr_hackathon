import requests
from bs4 import BeautifulSoup

URL = "https://www.indiatvnews.com/latest-news"
def india_tv_news_scraper(url: str = URL, max_articles: int = 10) -> list:    
    response = requests.get(url)

    if response.status_code == 200:
        news = []
        print("🔍 Searching for latest news on IndiaTV")
        soup = BeautifulSoup(response.text, "html.parser")
        columns = soup.find_all("div", class_="box")
        for column in columns[:-4]:
            links = [a['href'] for a in column.find_all("a", href=True)]

            ctr = 0
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
                        news.append({"title": title, "date_time": date_time, "content": full_content})
                        ctr += 1
                        if ctr >= 2:
                            break
                    else:
                        print(f"Failed to retrieve page, status code: {response.status_code}")
                        continue
                except requests.exceptions.Timeout:
                    print(f"Timeout error for link {link}")
                    continue
            
            print("Scraping complete. Total articles scraped:", len(news))
            return news
    else:
        print(f"Failed to retrieve page, status code: {response.status_code}")