from playwright.async_api import async_playwright
import asyncio

async def scrape_page_content():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        topic = "jee mains"
        print(f"🔍 Searching for: {topic}")
        await page.goto("https://www.livemint.com/search", timeout=60000)

        # Fill the search input field
        await page.fill("#searchField", topic)

        # Press Enter to search
        await page.press("#searchField", "Enter")

        # Wait for results to load
        await page.wait_for_selector(".listingNew")

        # Extract news article links
        links = await page.eval_on_selector_all(
            ".headline a",
            "elements => elements.map(el => el.href)"
        )
        await asyncio.sleep(5)
        print(f"✅ Found {len(links)} links for '{topic}'")
        await browser.close()

    return links

asyncio.run(scrape_page_content())