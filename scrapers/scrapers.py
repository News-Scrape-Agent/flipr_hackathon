import requests
from bs4 import BeautifulSoup


def indian_express_scraper(url: str,num_pages: int,num_articles: int):    
    response = requests.get(url)

    if response.status_code == 200:
        news = []
        soup = BeautifulSoup(response.text, "html.parser")
        div_class_name = "nation"
        page_class_name = "page-numbers"
        target_div = soup.find("div", class_=div_class_name)
        total_pages = soup.find_all("a", class_=page_class_name)[1].text
        links = []
        for i in range(1,min(num_pages,int(total_pages)+1)):
            try:
                page_response = requests.get(url + "page/" + str(i) + "/", timeout=6)
                if page_response.status_code == 200:
                    page_soup = BeautifulSoup(page_response.text, "html.parser")
                    target_div = page_soup.find("div", class_=div_class_name)
                    divs = target_div.find_all("div")
                    links.extend([a["href"] for div in divs for a in div.find_all("a", href=True)])
                else:
                    print(f"Failed to retrieve page, status code: {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"Timeout error for page {i}")
        links = set(links)
        filtered_links = [link for link in links if not link.startswith("https://indianexpress.com/latest-news/page/")]
        filtered_links = filtered_links[:min(num_articles,len(filtered_links))]
        for link in filtered_links:
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
                    news.append({"title": title, "date_time": date_time, "content": full_content})
                else:
                    print(f"Failed to retrieve page, status code: {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"Timeout error for link {link}")
        return news
    else:
        print(f"Failed to retrieve page, status code: {response.status_code}")

def india_tv_news_scraper(url: str):    
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
            for link in links:
                try:
                    link_response = requests.get(link, timeout=6)
                    if link_response.status_code == 200:
                        link_soup = BeautifulSoup(link_response.text, "html.parser")
                        headline = link_soup.find("h1", class_="arttitle")
                        title = headline.text
                        date_time = link_soup.find("time")["datetime"]
                        content_div = link_soup.find("div", class_="content", id = "content")
                        full_content = None
                        if content_div:
                            paragraphs = content_div.find_all("p")
                            full_content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                        news.append({"title": title, "date_time": date_time, "label":label,"content": full_content})
                    else:
                        print(f"Failed to retrieve page, status code: {response.status_code}")
                except requests.exceptions.Timeout:
                    print(f"Timeout error for link {link}")
        print("Scraping complete. Total articles:", len(news))
        return news
    else:
        print(f"Failed to retrieve page, status code: {response.status_code}")

# url = "https://indianexpress.com/latest-news/"
url = "https://www.indiatvnews.com/latest-news"
num_pages = 3
num_articles = 5
# indian_express_scraper(url, num_pages, num_articles)
news_list = india_tv_news_scraper(url)
