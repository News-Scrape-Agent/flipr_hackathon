import requests
from bs4 import BeautifulSoup

# URL of the website (Replace with the actual URL)
URL = "https://www.livemint.com/latest-news"

def livemint_scraper(url: str = URL, num_articles: int = 10) -> list:
    # Send a request to the website
    headers = {"User-Agent": "Mozilla/5.0"}
    news = []
    try:
        response = requests.get(url, headers=headers)

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all <li> elements with the given class
        articles = soup.find_all("div", class_="listingNew")

        links = []

        for article in articles:
            # Find the h2 tag inside div with class 'headline'
            h2_tag = article.find("h2", class_="headline")
            if h2_tag:
                # Find the <a> tag inside <h2>
                a_tag = h2_tag.find("a")
                if a_tag and "href" in a_tag.attrs:
                    link = a_tag["href"]
                    full_link = f"https://www.livemint.com{link}" if link.startswith("/") else link
                    links.append(full_link)

        # # Print extracted links
        # for idx, link in enumerate(links, 1):
        #     print(f"{idx}. {link}")

        links = links[:min(num_articles,len(links))]
        for url in links:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # Parse the HTML content of the webpage
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract the <h2> tag content
                    h1_tag = soup.find('h1', id="article-0")
                    h1_text = h1_tag.get_text() if h1_tag else 'No <h1> tag found'

                    # Extract all text content from story_para_ classes
                    story_paras = soup.find_all('div', class_="storyParagraph", id=lambda x: x and x.startswith('article-index'))
                    story_texts = [para.get_text() for para in story_paras]
                    article_text = ' '.join(story_texts)

                    # Extract the "First Published" date and time
                    first_published = soup.find('div', class_=lambda x: x and x.startswith('storyPage_date'))
                    first_published_text = first_published.get_text(strip=True) if first_published else 'No First Published date found'

                    news.append({'title': h1_text, 'date_time': first_published_text, 'content': article_text})
                else:
                    print(f"Failed to retrieve the article, status code: {response.status_code}")
                    continue
            except:
                print(f"An error occurred while scraping the article: {url}")
                continue
    except:
        print("An error occurred while scraping the website.")
        
    print("Scraping complete. Total articles:", len(news))
    return news