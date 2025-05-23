# Installation instructions:
#   pip install spacy pandas rapidfuzz geopy
#   python -m spacy download en_core_web_trf
#   python -m spacy download en_core_web_sm

import ast
import pandas as pd
import spacy
from rapidfuzz import process, fuzz
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Load city-state data
df = pd.read_csv("indian_cities_and_states.csv")

# Prepare lookup structures
cities = df['City'].str.lower().tolist()
states = df['State'].str.lower().unique().tolist()
city_to_state = dict(zip(df['City'].str.lower(), df['State'].str.lower()))

# Load SpaCy NER model with fallback
def load_spacy_model(preferred: str = "en_core_web_trf", fallback: str = "en_core_web_sm"):
    try:
        return spacy.load(preferred)
    except OSError:
        print(f"[Warning] SpaCy model '{preferred}' not found, loading '{fallback}'.")
        return spacy.load(fallback)

nlp = load_spacy_model()

# Configure Nominatim geocoder (open-source, no usage restrictions)
geolocator = Nominatim(user_agent="location_extractor")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)


def extract_locations_with_model(text: str) -> list:
    """
    Uses SpaCy NER to extract location spans, then geocodes each span via OpenStreetMap
    to get canonical name, type, and state/country information. Handles typos and unseen places.
    Returns list of location names (strings).
    """
    doc = nlp(text)
    names = []

    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            span = ent.text
            loc = geocode(span)
            if loc:
                names.append(loc.address)
    return names

def correct_city_typo(city_name: str, city_list: list, state_list: list, threshold: int = 60) -> str:
    """
    Uses fuzzy matching to correct city name typos.
    Returns the best match if above threshold, else returns the original.
    """
    match_city, score_city, _ = process.extractOne(city_name.lower(), city_list, scorer=fuzz.ratio)
    match_state, score_state, _ = process.extractOne(city_name.lower(), state_list, scorer=fuzz.ratio)

    if score_city >= score_state and score_city >= threshold:
        return match_city.lower()
    elif score_state >= score_city and score_state >= threshold:
        return match_state.lower()
    return match_state.lower()


def find_location_in_user_query(args: dict, user_query: str) -> list:
    """
    If args provide a location, correct typos and return the city or state name.
    Otherwise, tries to extract locations from user query, correct typos, and return city or state names.
    """
    locations = []
    if args.get('location'):
        loc = args['location'].strip()
        corrected_loc = correct_city_typo(loc, cities, states)
        locations.append(corrected_loc.title())
    else:
        extracted = extract_locations_with_model(user_query)
        for loc in extracted:
            for city in cities:
                if city in loc.lower():
                    corrected_loc = correct_city_typo(city, cities, states)
                    locations.append(corrected_loc.title())
                    break
    return locations


def normalize_topic_param(topic) -> list:
    """
    Ensures that the 'topic' parameter is always a list of strings.
    """
    if topic is None:
        return []
    if isinstance(topic, list):
        return topic
    if isinstance(topic, str):
        try:
            parsed = ast.literal_eval(topic)
            if isinstance(parsed, list):
                return [t.strip() for t in parsed if isinstance(t, str)]
        except Exception:
            pass
        return [t.strip() for t in topic.split(',') if t.strip()]
    return []
