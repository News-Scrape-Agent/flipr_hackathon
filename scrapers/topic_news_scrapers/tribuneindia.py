import asyncio
from playwright.async_api import async_playwright

async def scrape_links():
    async with async_playwright() as p:
        # Launch a browser instance (headless=True for background execution)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Open the target URL
        url = "https://www.tribuneindia.com/topic/ai"
        await page.goto(url, timeout=60000)  # 60 sec timeout

        # Wait for elements to load
        await page.wait_for_selector("div.post-item.search_post", timeout=10000)

        # Extract all links
        links = await page.eval_on_selector_all(
            "div.post-featured-img-wrapper a",  # Target elements
            "elements => elements.map(el => el.href)"
        )

        # Print the extracted links
        for link in links:
            print(link)

        # Close the browser
        await browser.close()

# Run the async function
asyncio.run(scrape_links())
