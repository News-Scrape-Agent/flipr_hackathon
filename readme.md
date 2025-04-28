# News Aggregator & Blog Publishing System

## Video
https://github.com/user-attachments/assets/03560c5d-3cba-413f-bc03-80156082d9d9

## 📋 Overview
An automated pipeline that:
1. Scrapes news from websites 
2. Clusters articles into categories (Sports, Entertainment, etc.)
3. Processes through LLM for user interactions
4. Generates & translates blogs
5. Publishes to WordPress

## 🚀 Key Features
- **Smart Scraping**  
  Location-based news scraping (e.g. "Delhi news")
- **AI Clustering**  
  BERT-based categorization into predefined labels
- **LLM Interaction**  
  Natural language queries and blog generation
- **WordPress Integration**  
  Direct publishing with OAuth2 authentication
- **Translation API**  
  MyMemory API integration for multi-language support

## ⚙️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/Yash-g2310/flipr_hackathon.git
cd flipr_hackathon
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.env` file with:

```ini
# WordPress OAuth2 Credentials
WORDPRESS_CLIENT_ID=<your_client_id>
WORDPRESS_CLIENT_SECRET=<your_client_secret>
WORDPRESS_USERNAME=<wp_username>
WORDPRESS_PASSWORD=<wp_password>
WORDPRESS_REDIRECT_URI=http://localhost:8000/callback
WORDPRESS_SITE_URL=<your_site_url>

# Translation Service
MYMEMORY_TRANSLATE_KEY=<your_api_key>

# Model Configuration 
MODEL_DIR=bert_model
TF_ENABLE_ONEDNN_OPTS=0
```

### 🔑 Obtaining Credentials

#### WordPress Keys:
1. Create an app at [WordPress Developer Portal](https://developer.wordpress.com/apps/)
2. Get `CLIENT_ID` and `CLIENT_SECRET`
3. Use your WordPress login for `USERNAME/PASSWORD`
4. Set `REDIRECT_URI` to your callback URL

#### Translation API:
1. Register at [MyMemory API](https://mymemory.translated.net/doc/spec.php)
2. Get a free API key for `MYMEMORY_TRANSLATE_KEY`

## 🖥️ Usage

### Start System
1. Download and install Ollama
2. Download Llama3.2 3B model into Ollama using:
```bash
ollama run llama3.2:3b
```
then run the follwing commands:
```bash
ollama serve
chainlit run app.py
```

### Enter Query
```plaintext
> Give me latest news in Delhi
```

### System Will:
- Scrape location-specific news
- Cluster into categories
- Show summarized articles
- Translate summarized articles into desired language
- Publish translated articles onto Wordpress

## 🔄 Workflow  
The system processes user queries using a **self-hosted Llama 3.2 3B model (via Ollama)** to extract four key parameters: **Latest News, Topics, Language, and Location**. If the model does not return parameters in the expected format, a **manual extraction script** (`process_user_query.py`) ensures accuracy. Based on these parameters, three specialized **scrapers** fetch news articles, categorized by **latest news, specific locations, or topics of interest**.  

Once articles are collected, they are **summarized using the LLM**, which generates **titles and structured blog content**. If translation is required, each blog is divided into **250-character chunks**, sent to the **MyMemory API for translation**, and then reassembled. Finally, the translated or original blogs are **published to WordPress** using **OAuth2 authentication**, ensuring a seamless **end-to-end automated news-to-blog pipeline**. 🚀  


## 🔮 Future Roadmap
- Enhanced NLP clustering accuracy
- Multi-source news integration
- Custom blog templates
- Social media auto-posting
- Sentiment analysis layer
