import os
import yfinance as yf
import pandas as pd
from flask import Flask, render_template, request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
import plotly.express as px
import logging

# Configure logging
logging.basicConfig(filename='logs/app.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

app = Flask(__name__)

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to fetch stock data
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")  # Fetch 1 month of data
        return data
    except Exception as e:
        logging.error(f"Error fetching stock data: {e}")
        return None

# Function to fetch news articles
def get_news_articles(ticker):
    api_key = os.getenv("NEWS_API_KEY")  # Use environment variable for API key
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [article["title"] for article in articles[:5]]  # Limit to 5 articles
    else:
        logging.error(f"Error fetching news: {response.status_code}")
        return []

# Function to perform sentiment analysis
def analyze_sentiment(news_articles):
    sentiments = []
    for article in news_articles:
        score = analyzer.polarity_scores(article)
        if score['compound'] >= 0.05:
            sentiment = "Positive"
        elif score['compound'] <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        sentiments.append(sentiment)
    return sentiments

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ticker = request.form["ticker"]
        try:
            # Fetch stock data
            stock_data = get_stock_data(ticker)
            if stock_data is None:
                return render_template("index.html", error="Failed to fetch stock data.")
            
            current_price = stock_data['Close'].iloc[-1]
            fig = px.line(stock_data, x=stock_data.index, y='Close', title=f"{ticker} Historical Prices")
            graph_html = fig.to_html(full_html=False)

            # Fetch news articles
            news_articles = get_news_articles(ticker)
            sentiments = analyze_sentiment(news_articles)

            return render_template("index.html", 
                                   ticker=ticker, 
                                   price=current_price, 
                                   graph=graph_html,
                                   news=zip(news_articles, sentiments))
        except Exception as e:
            logging.error(f"Error in index route: {e}")
            return render_template("index.html", error=str(e))
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)