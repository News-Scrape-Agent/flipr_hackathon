import requests
from bs4 import BeautifulSoup

def indian_express_cities_scraper(url: str):    
    response = requests.get(url)

    if response.status_code == 200:
        news = []
        soup = BeautifulSoup(response.text, "html.parser")
        target_ul = soup.find("ul", class_="page_submenu")
        cities_url = [url+(str(a.text).lower())+'/' for a in target_ul.find_all("a", href=True)]
        cities_url = cities_url[1:]
        for city_url in cities_url:
            try:
                city_response = requests.get(city_url, timeout=6)
                if city_response.status_code == 200:
                    city_soup = BeautifulSoup(city_response.text, "html.parser")
                    new_div = city_soup.find("div", id="north-east-data")
                    news_link = [a["href"] for a in new_div.find_all("a", href=True)]
                    news_link = list(set(news_link))
                    news_link = news_link[:10]
                    for link in news_link:
                        try:
                            link_response = requests.get(link, timeout=6)
                            if link_response.status_code == 200:
                                link_soup = BeautifulSoup(link_response.text, "html.parser")
                                headline = link_soup.find("h1", itemprop="headline")
                                title = headline.text
                                date_time = link_soup.find("span", itemprop="dateModified")["content"]
                                content_div = link_soup.find("div", id="pcl-full-content")
                                full_content = None
                                if content_div:
                                    paragraphs = content_div.find_all("p")
                                    full_content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                                news.append({"title": title, "date_time": date_time, "city": city_url.split('/')[-2], "content": full_content})
                            else:
                                print(f"Failed to retrieve page, status code: {response.status_code}")
                                continue
                        except requests.exceptions.Timeout:
                            print(f"Timeout error for {link}")
                            continue
                else:
                    print(f"Failed to retrieve page, status code: {response.status_code}")
                    continue
            except requests.exceptions.Timeout:
                print(f"Timeout error for {city_url}")
                continue
        return news
    
    else:
        print(f"Failed to retrieve page, status code: {response.status_code}")
        
        
def india_tv_news_cities_scraper(url: str):
    response = requests.get(url)

    if response.status_code == 200:
        news = []
        soup = BeautifulSoup(response.text, "html.parser")
        state_divs = soup.find_all("div", class_="box")
        state_div = state_divs[-1]
        state_links = [a["href"] for a in state_div.find_all("a", href=True)]
        for state_link in state_links:
            try:
                state_response = requests.get(state_link, timeout=6)
                if state_response.status_code == 200:
                    state_soup = BeautifulSoup(state_response.text, "html.parser")
                    news_ul = state_soup.find_all("ul", class_="news-list")
                    news_links = [a["href"] for news_div in news_ul for a in news_div.find_all("a", href=True)]
                    news_links = list(set(news_links))
                    news_links = news_links[:10]
                    for news_link in news_links:
                        if(len(news_link.split('/')) !=5):
                            continue
                        try:
                            news_response = requests.get(news_link, timeout=6)
                            if news_response.status_code == 200:
                                news_soup = BeautifulSoup(news_response.text, "html.parser")
                                headline = news_soup.find("h1", class_="arttitle")
                                title = headline.text
                                date_time = news_soup.find("time")
                                if date_time:
                                    date_time = date_time["datetime"]
                                else:
                                    date_time = None
                                content_div = news_soup.find("div", class_="content", id = "content")
                                full_content = None
                                if content_div:
                                    paragraphs = content_div.find_all("p")
                                    full_content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                                news.append({"title": title, "date_time": date_time, "state": state_link.split('/')[-1], "content": full_content})
                            else:
                                print(f"Failed to retrieve page, status code: {response.status_code}")
                                continue
                        except requests.exceptions.Timeout:
                            print(f"Timeout error for {news_link}")
                            continue
                else:
                    print(f"Failed to retrieve page, status code: {response.status_code}")
                    continue
            except requests.exceptions.Timeout:
                print(f"Timeout error for {state_link}")
                continue
        return news
    else:
        print(f"Failed to retrieve page, status code: {response.status_code}")
        
# url = "https://indianexpress.com/section/cities/"
url = "https://www.indiatvnews.com/"

news = india_tv_news_cities_scraper(url)
print(news)

