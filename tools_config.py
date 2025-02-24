tools = [
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
                        "type": "string",
                    },
                    "enum": [
                        "elections and politics", "sports", "crime and war", "science and technology", "astrology", 
                        "business", "entertainment", "health and medicine", "environment", 
                        "education", "world news", "lifestyle and culture", "jobs"
                    ],
                    "description": "The specific news topic the user is interested in, if applicable."
                },
                "location": {
                    "type": "string",
                    "description": "The location for which the user wants news, if applicable."
                },
                "language": {
                    "type": "string",
                    "description": "The language in which the user wants news, if applicable."
                },
            },
            "required": ["latest_news", "topic"]
        }
    },
]
