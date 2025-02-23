import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://www.britannica.com/topic/list-of-cities-and-towns-in-India-2033033"
response = requests.get(url)

# Parse the HTML content of the webpage
soup = BeautifulSoup(response.content, 'html.parser')

data = []

# Find all sections with data-level="1"
sections = soup.find_all('section', {'data-level': '1'}, id=lambda x: x and x.startswith("ref328"))

for section in sections:
    state_name = section.find('h2', class_='h1').get_text(strip=True)
    cities = [li.get_text(strip=True) for li in section.find_all('li')]
    
    # Append each city with its corresponding state
    for city in cities:
        data.append([state_name, city])  # Each row is [state, city]

# Create a DataFrame
df = pd.DataFrame(data, columns=['State', 'City'])

# Save to CSV if needed
df.to_csv("indian_cities_and_states.csv", index=False)