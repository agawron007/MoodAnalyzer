
from textblob import TextBlob

def calculate_mood_text_blob(text):
    analysis = TextBlob(text)
    sentiment = classify_sentiment(analysis)
    print "Mood (0-Negative, 0.5 Neutral, 1 - Positive: " + str(sentiment) + "\n"
    return sentiment

def classify_sentiment(analysis, threshold = 0):
    # classify sentiment polarity as positive or negative

    if analysis.sentiment.polarity > threshold:
        return 1.0
    elif analysis.sentiment.polarity < threshold:
        return 0 * 1.0
    else:
        return 0.5