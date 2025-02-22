tools = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "get_conversational_response",
        "description": "Respond conversationally if no other tools should be called for a given query.",
        "parameters": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "Conversational response to the user.",
                },
            },
            "required": ["response"],
        },
    },
    {
        "name": "analyze_news_query",
        "description": "Analyze the user query to determine whether they want the latest news or news on a specific topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "latest_news": {
                    "type": "boolean",
                    "description": "True if the user wants the latest general news, False if they want news on a specific topic."
                },
                "topic": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "enum": ["Politics", "Sports", "Crime", "Science and Technology", "Business", "Entertainment", "Health", "Environment", "Education", "Global News", "Local News", "Lifestyle and Culture"],
                    "description": "The specific news topic the user is interested in, if applicable."
                },
                "location": {
                    "type": "string",
                    "description": "The location for which the user wants news, if applicable."
                }
            },
            "required": ["latest_news", "topic"]
        }
    },
]
