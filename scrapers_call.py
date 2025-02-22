"""
This script is used to call the scrapers for the different websites as per LLMs Response of User's Query.
Features:
1) If Latest News is True and Topic is Empty then it will run all the scrapers and will fetch atmost 2 news from each category.
2) If Topic is not Empty then it will run the scrapers for the given topic and will fetch news as per no. of topics.
3) If Location is not Empty then it will run only selected scrapers and will collect news of that place.
4) This script will return the news in the form of a list of dictionaries or a Dataframe. 
5) Data from this script will go for Blog Generation.
"""