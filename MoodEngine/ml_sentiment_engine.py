from textblob import TextBlob

def classify_sentiment(analysis, threshold = 0):
    # classify sentiment polarity as positive or negative

    if analysis.sentiment.polarity > threshold:
        return 1.0
    elif analysis.sentiment.polarity < threshold:
        return 0.5
    else:
        return 0.0

class TextBlobSentimentEngine:
    @staticmethod
    def calculate(text):
        analysis = TextBlob(text)
        return classify_sentiment(analysis)

