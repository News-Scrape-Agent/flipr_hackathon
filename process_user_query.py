import ast
import difflib
import pandas as pd


df = pd.read_csv("indian_cities_and_states.csv")
# Convert to lowercase for case-insensitive matching
cities = df["City"].str.lower().tolist()
states = df["State"].str.lower().tolist()


def find_location_in_user_query(args: dict, user_query: str) -> list:
    if "location" in args and args["location"]:
        return [args["location"].lower()]
    
    query_words = user_query.lower().split()  # Tokenizing query
    locations = set()
    # Check for city matches
    city_match = difflib.get_close_matches(" ".join(query_words), cities, n=1, cutoff=0.8)
    if city_match:
        return locations.add(city_match[0])

    # Check for state matches
    state_match = difflib.get_close_matches(" ".join(query_words), states, n=1, cutoff=0.8)
    if state_match:
        return locations.add(state_match[0])

    if not locations:
        return []  # No location found
    
    return list(locations)


def normalize_topic_param(topic) -> list:
    """
    Ensures that the 'topic' parameter is always a list of strings.
    If the model mistakenly returns a string, it converts it into a valid list.
    """
    if topic is None:
        return []
    
    if isinstance(topic, list):
        return topic  # Already a valid list
    
    if isinstance(topic, str):
        try:
            # Case 1: If it's a string representation of a list, safely evaluate it
            parsed_topic = ast.literal_eval(topic)
            if isinstance(parsed_topic, list):
                return [t.strip() for t in parsed_topic if isinstance(t, str)]
        except (SyntaxError, ValueError):
            pass  # Not a list representation, move to next check
        
        # Case 2: If it's a comma-separated string, split it
        return [t.strip() for t in topic.split(",") if t.strip()]

    return []