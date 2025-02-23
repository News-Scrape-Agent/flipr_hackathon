import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

url = "https://indianexpress.com/search/"
async def indian_express_topic_scraper(url: str = url, topics: list = [], max_articles: int = 10) -> list:
    news = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        for topic in topics:
            print(f"🔍 Searching for: {topic}")
            await page.goto(url, timeout=60000)

            # Fill the search input field
            await page.fill(".srch-npt", topic)

            # Click the search button
            await page.click(".srch-btn")

            # Wait for search results
            await page.wait_for_selector("#search-listing-results .search-result")

            # Extract valid news article links
            links = await page.eval_on_selector_all(
                "#search-listing-results .search-result h3 a",
                "elements => elements.map(el => el.href)"
            )

            # print(f"Found {len(links)} links for '{topic}'")
            links = links[:min(max_articles, len(links))]
            for link in links:
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
                            
                        news.append({"title": title, "date_time": date_time, "content": full_content, "topic": topic})
                    else:
                        print(f"Failed to retrieve page, status code: {link_response.status_code}")
                        continue
                except requests.exceptions.Timeout:
                    print(f"Timeout error for {link}")
                    continue

        await browser.close()

    return news
