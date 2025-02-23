import requests
from bs4 import BeautifulSoup

url = "https://indianexpress.com/section/cities/"
def indian_express_cities_scraper(url: str, max_articles: int = 10):  
    try:  
        response = requests.get(url)
    except Exception as e:
        print(f"Error getting the response from {url}: {e}")
        return []

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
                    news_link = news_link[:min(max_articles, len(news_link))]
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
                                news.append({"title": title, "date_time": date_time, "content": full_content, "city": city_url.split('/')[-2]})
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
    
    else:
        print(f"Failed to retrieve page, status code: {response.status_code}")
        
    print("Scraping complete. Total articles:", len(news))
    return news