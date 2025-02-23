import asyncio
from playwright.sync_api import sync_playwright

# # url = "https://timesofindia.indiatimes.com/astrology/horoscope/aquarius-daily-horoscope-today-february-19-2025-businesspersons-can-explore-new-ventures/articleshow/118364304.cms"
# # url = "https://indianexpress.com/todays-paper/2025/02/19/"
# url = "https://www.livemint.com/latest-news"

# def scrape_page_content(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # Set headless=False to see the browser
#         page = browser.new_page()
#         page.goto(url, timeout=60000)  # Wait for full page load

#         # Extract the main content (adjust selector as needed)
#         content = page.inner_text("body")

#         print(content)  # Display the extracted content
#         browser.close()

# scrape_page_content(url)


# import asyncio
# from playwright.async_api import async_playwright

# url = "https://www.sportskeeda.com/cricket/news-he-focuses-keeping-icc-ranking-intact-danish-kaneria-pakistan-spinner-lashes-babar-azam-ahead-ind-vs-pak-2025-champions-trophy-clash"

# async def main():
#     async with async_playwright() as p:
#         # Launch the browser
#         browser = await p.chromium.launch(headless=True)  # Run in headless mode for faster execution
#         page = await browser.new_page()
        
#         # Go to the webpage
#         await page.goto(url)
#         await page.wait_for_load_state("domcontentloaded")  # Ensures the page content is fully loaded
        
#         # Extract article content
#         article_content = []
#         paragraphs = await page.locator('p[data-imp-id^="article_paragraph"]').all()

#         for p in paragraphs:
#             p_text = await p.text_content()
#             if p_text:
#                 article_content.append(p_text.strip())

#         # Close the browser
#         await browser.close()

#     # Print or return extracted text
#     return "\n".join(article_content)

# # Run the Playwright script
# asyncio.run(main())



