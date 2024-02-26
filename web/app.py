from flask import Flask, request, render_template
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# URL of the Telegram Service
TELEGRAM_SERVICE_URL = 'http://18.215.248.144:8001/webhook'

# Initialize the sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Global variables to store the latest message and its sentiment
latest_alert_message = "No alerts triggered yet."
latest_sentiment = ""

@app.route('/')
def index():
    return render_template('index.html', alert_message=latest_alert_message, sentiment=latest_sentiment)

@app.route('/trigger', methods=['POST'])
def trigger_alert():
    # Simulate the trigger by sending a POST request to Telegram Service
    response = requests.post(TELEGRAM_SERVICE_URL, data="Alert triggered")
    if response.status_code == 200:
        return "Alert triggered successfully"
    else:
        return "Failed to trigger alert"

@app.route('/update_message', methods=['POST'])
def update_message():
    global latest_alert_message, latest_sentiment
    # Update the latest message with the data received from the request
    latest_alert_message = request.data.decode('utf-8')
    
    # Perform sentiment analysis based on keywords indicating profit or loss
    if 'profit' in latest_alert_message.lower():
        latest_sentiment = "Positive"
    elif 'loss' in latest_alert_message.lower():
        latest_sentiment = "Negative"
    else:
        # Perform sentiment analysis using VADER if keywords are not found
        sentiment_score = analyzer.polarity_scores(latest_alert_message)
        if sentiment_score['compound'] >= 0.05:
            latest_sentiment = "Positive"
        elif sentiment_score['compound'] <= -0.05:
            latest_sentiment = "Negative"
        else:
            latest_sentiment = "Neutral"
    
    return "Message updated successfully"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
