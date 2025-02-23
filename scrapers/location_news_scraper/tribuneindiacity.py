import asyncio
from playwright.async_api import async_playwright

states = ["Punjab", "Haryana", "Himachal Pradesh", "J K", "Uttarakhand", "Uttar Pradesh", "Rajasthan", "Madhya Pradesh", "Chhattisgarh"]

cities = ["Amritsar", "Bathinda", "Chandigarh", "Delhi", "Jalandhar", "Ludhiana", "Patiala", "Shaharnama"]

base_url = "https://www.tribuneindia.com/news/"
extracted_links = []
article_contents = []
async def scrape_links():
    async with async_playwright() as p:
        # Launch a browser instance (headless=True for background execution)
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        for state in states:
            # Open the target URL
            url = "https://www.tribuneindia.com/news/state/" + state.lower().replace(" ", "-")
            await page.goto(url, timeout=60000)  # 60 sec timeout

            # Wait for elements to load
            await page.wait_for_selector("article.card-df h2 a", timeout=10000)

            # Extract all article links inside <h2>
            links = await page.eval_on_selector_all(
                "article.card-df h2 a",  # Targeting <a> inside <h2>
                "elements => elements.map(el => el.href)"
            )
            extracted_links.append(links)
        
        for city in cities:
            url = "https://www.tribuneindia.com/news/city/" + city.lower()
            await page.goto(url, timeout=60000)

            await page.wait_for_selector("article.card-df h2 a", timeout=10000)

            # Extract all article links inside <h2>
            links = await page.eval_on_selector_all(
                "article.card-df h2 a",  # Targeting <a> inside <h2>
                "elements => elements.map(el => el.href)"
            )
            extracted_links.append(links)

        # Close the browser
        await browser.close()


async def scrape_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for links in extracted_links:
            articles = []
            for url in links:
                # Replace with the actual URL
                await page.goto(url, timeout=60000)

                # Scrape text from h1 tag with class post-header
                h1_text = await page.text_content('h1.post-header')
                print('H1 Text:', h1_text)

                # Scrape text from p tags inside div with class story-detail
                p_elements = await page.query_selector_all('div.story-detail p')
                p_texts_content = [await p.text_content() for p in p_elements]
                # print('Paragraph Texts:', p_texts_content)
                article = ' '.join(p_texts_content)
                articles.append(article)
                
            article_contents.append

        await browser.close()


# Run the async function
asyncio.run(scrape_links())

# Run the async function
asyncio.run(scrape_data())