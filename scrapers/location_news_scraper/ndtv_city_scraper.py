import requests
from bs4 import BeautifulSoup

def ndtv_cities_scraper(url):
    news = []
    response = requests.get(url, timeout=60)
    if response.status_code != 200:
        print("Failed to load main page")
        return [], news

    soup = BeautifulSoup(response.text, "html.parser")
    metro_elements = soup.select("div.dd-nav_in:not(.dd-nav_in-1-fl) ul.dd-nav_ul li a")
    metros = [a.get("href") for a in metro_elements if a.get("href")][4:8]
    
    other_elements = soup.select("div.dd-nav_in.dd-nav_in-1-fl ul.dd-nav_ul li a")
    other_cities = [a.get("href") for a in other_elements if a.get("href")]
    
    cities_links = metros + other_cities

    for city_link in cities_links:
        try:
            city_resp = requests.get(city_link, timeout=60)
            if city_resp.status_code != 200:
                continue
            city_soup = BeautifulSoup(city_resp.text, "html.parser")
            
            news_links_elements = city_soup.select(".NwsLstPg_ttl-lnk")
            
            links = list({a.get("href") for a in news_links_elements if a.get("href")})
            links = links[:1]
            if links:
                article_link = links[0]
                try:
                    article_resp = requests.get(article_link, timeout=60)
                    if article_resp.status_code != 200:
                        continue
                    article_soup = BeautifulSoup(article_resp.text, "html.parser")
                    
                    heading_elem = article_soup.select_one("h1.sp-ttl")
                    heading = heading_elem.get_text(strip=True) if heading_elem else ""
                    
                    time_elem = article_soup.select_one("span.pst-by_lnk")
                    time_text = time_elem.get_text(strip=True) if time_elem else ""
                    
                    parts = article_link.split("/")
                    label = parts[3] if len(parts) > 3 else ""
                    
                    paragraphs = article_soup.select("div.Art-exp_cn p")
                    content = " ".join(p.get_text(strip=True) for p in paragraphs)
                    
                    news.append({
                        "title": heading,
                        "date_time": time_text,
                        "label": label,
                        "location": label[:-5],
                        "content": content
                    })
                except Exception as e:
                    # If any error occurs while scraping the article, skip it.
                    continue
        except Exception as e:
            continue
    
    return news

if __name__ == "__main__":
    url = "https://www.ndtv.com/"
    articles = ndtv_cities_scraper(url)
    print("\nScraped News Articles:")
    for article in articles:
        print(article)
