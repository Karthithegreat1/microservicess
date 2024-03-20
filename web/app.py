from flask import Flask, request, render_template, make_response
import requests
from io import BytesIO
from reportlab.pdfgen import canvas
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# URL of the Telegram Service
TELEGRAM_SERVICE_URL = 'http://54.237.101.72:8001/webhook'

# Initialize the sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Global variables to store the latest messages and their sentiments
latest_alert_messages = ["No alerts triggered yet."] * 5
latest_sentiments = [""] * 5

@app.route('/')
def index():
    messages_with_info = [extract_info(message) for message in latest_alert_messages]
    messages_with_sentiments = zip(messages_with_info, latest_sentiments)
    return render_template('index.html', messages_with_sentiments=messages_with_sentiments)

@app.route('/update_message', methods=['POST'])
def update_message():
    global latest_alert_messages, latest_sentiments
    # Shift the existing messages and sentiments by one position
    latest_alert_messages = latest_alert_messages[1:] + [request.data.decode('utf-8')]
    
    # Perform sentiment analysis based on keywords indicating profit or loss
    for i, message in enumerate(latest_alert_messages):
        if 'profit' in message.lower():
            latest_sentiments[i] = "Positive"
        elif 'loss' in message.lower():
            latest_sentiments[i] = "Negative"
        else:
            # Perform sentiment analysis using VADER if keywords are not found
            sentiment_score = analyzer.polarity_scores(message)
            if sentiment_score['compound'] >= 0.05:
                latest_sentiments[i] = "Positive"
            elif sentiment_score['compound'] <= -0.05:
                latest_sentiments[i] = "Negative"
            else:
                latest_sentiments[i] = "Neutral"
    
    return "Messages updated successfully"

@app.route('/download_pdf')
def download_pdf():
    # Create a PDF dynamically
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)

    # Write the latest messages and their sentiments to the PDF
    y_position = 750
    for message, sentiment in zip(latest_alert_messages, latest_sentiments):
        entry_point, symbol, entry_price = extract_info(message)
        c.drawString(50, y_position, f"Entry Point: {entry_point}")
        c.drawString(50, y_position - 20, f"Symbol: {symbol}")
        c.drawString(50, y_position - 40, f"Entry Price: {entry_price}")
        c.drawString(50, y_position - 60, f"Sentiment: {sentiment}")
        y_position -= 80

    c.save()

    # Prepare the response with PDF data
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=latest_alerts.pdf'
    response.headers['Content-Type'] = 'application/pdf'

    return response

def extract_info(text):
    entry_point = None
    symbol = None
    entry_price = None
    lines = text.split('\n')
    for line in lines:
        if 'position' in line.lower():
            entry_point = line.split(':')[1].strip()
        elif 'symbol' in line.lower():
            symbol = line.split(':')[1].strip()
        elif 'entry price' in line.lower():
            entry_price = line.split(':')[1].strip()
    return entry_point, symbol, entry_price

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
