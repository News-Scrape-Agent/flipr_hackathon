import requests
from bs4 import BeautifulSoup

URL = "https://indianexpress.com/latest-news"
def indian_express_scraper(url: str = URL, num_pages: int = 3, num_articles: int = 5) -> list:    
    response = requests.get(url)

    if response.status_code == 200:
        news = []
        print("🔍 Searching for latest news on Indian Express")
        soup = BeautifulSoup(response.text, "html.parser")
        div_class_name = "nation"
        page_class_name = "page-numbers"
        target_div = soup.find("div", class_=div_class_name)
        total_pages = soup.find_all("a", class_=page_class_name)[1].text

        links = []
        for i in range(1, min(num_pages, int(total_pages)) + 1):
            try:
                page_response = requests.get(f"{url}/page/{i}/", timeout=6)
                if page_response.status_code == 200:
                    page_soup = BeautifulSoup(page_response.text, "html.parser")
                    target_div = page_soup.find("div", class_=div_class_name)
                    divs = target_div.find_all("div")
                    links.extend([a["href"] for div in divs for a in div.find_all("a", href=True)])
                else:
                    print(f"Failed to retrieve page, status code: {response.status_code}")
                    continue
            except requests.exceptions.Timeout:
                print(f"Timeout error for page {i}")
                continue

        links = list(set(links))

        filtered_links = links[:min(num_articles, len(links))]
        for link in filtered_links:
            try:
                link_response = requests.get(link, timeout=6)
                if link_response.status_code == 200:
                    link_soup = BeautifulSoup(link_response.text, "html.parser")
                    headline = link_soup.find("h1", itemprop="headline")
                    title = headline.get_text(strip=True) if headline else "N/A"

                    date_time_element = link_soup.find("span", itemprop="dateModified")
                    date_time = date_time_element.get("content", "N/A") if date_time_element else "N/A"

                    content_div = link_soup.find("div", id="pcl-full-content")
                    full_content = None
                    
                    if content_div:
                        paragraphs = content_div.find_all("p")
                        full_content = "\n".join(p.get_text(strip=True) for p in paragraphs)

                    news.append({"title": title, "date_time": date_time, "content": full_content})

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