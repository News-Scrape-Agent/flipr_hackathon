from playwright.sync_api import sync_playwright

class IndianExpressScraper:
    def __init__(self, headless=True):
        """Initialize Playwright with optional headless mode."""
        self.headless = headless

    def scrape_links(self, topics):
        """
        Searches for multiple topics on Indian Express and extracts news article links.
        
        :param topics: List of topics to search.
        :return: Dictionary where each topic maps to a list of article links.
        """
        results = {}

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            for topic in topics:
                print(f"🔍 Searching for: {topic}")
                page.goto("https://indianexpress.com/search/", timeout=60000)

                # Fill the search input field
                page.fill(".srch-npt", topic)

                # Click the search button
                page.click(".srch-btn")

                # Wait for search results
                page.wait_for_selector("#search-listing-results .search-result")

                # Extract valid news article links
                links = page.eval_on_selector_all(
                    "#search-listing-results .search-result h3 a",
                    "elements => elements.map(el => el.href)"
                )

                results[topic] = links
                print(f"Found {len(links)} links for '{topic}'")

            browser.close()

        return results

# Example Usage
topics_to_search = ["JEE Mains", "NEET 2025"]
scraper = IndianExpressScraper(headless=True)  # Set headless=True to run in background
news_links = scraper.scrape_links(topics_to_search)

# Print results
for topic, links in news_links.items():
    print(f"{topic}:")
    for link in links:
        print(f" - {link}")
