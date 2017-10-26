import os
import re
import logging
import pandas as pd
import numpy as np
import nltk.data
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from gensim.models import word2vec
from sklearn import naive_bayes, svm, preprocessing
from sklearn.decomposition import TruncatedSVD
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.cross_validation import cross_val_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection.univariate_selection import chi2, SelectKBest

#os.chdir("/Users/BradLi/Documents/Data Science/Kaggle/Sentiment")
#os.chdir("D:/OneDrive/PROJECTS/unicest-apps/bitcoins/sentiment.analysis-master")

##################### Initialization #####################

write_to_csv = True

# term_vector_type = {"TFIDF", "Binary", "Int", "Word2vec", "Word2vec_pretrained"}
# {"TFIDF", "Int", "Binary"}: Bag-of-words model with {tf-idf, word counts, presence/absence} representation
# {"Word2vec", "Word2vec_pretrained"}: Google word2vec representation {without, with} pre-trained models
# Specify model_name if there's a pre-trained model to be loaded
vector_type = "TFIDF"
model_name = "GoogleNews-vectors-negative300.bin"

# model_type = {"bin", "reg"}
# Specify whether pre-trained word2vec model is binary
model_type = "bin"
   
# Parameters for word2vec
# num_features need to be identical with the pre-trained model
num_features = 300    # Word vector dimensionality                      
min_word_count = 40   # Minimum word count to be included for training                      
num_workers = 4       # Number of threads to run in parallel
context = 10          # Context window size                                                                                    
downsampling = 1e-3   # Downsample setting for frequent words

# training_model = {"RF", "NB", "SVM", "BT", "no"}
training_model = "NB"

# feature scaling = {"standard", "signed", "unsigned", "no"}
# Note: Scaling is needed for SVM
scaling = "no"

# dimension reduction = {"SVD", "chi2", "no"}
# Note: For NB models, we cannot perform truncated SVD as it will make input negative
# chi2 is the feature selectioin based on chi2 independence test
dim_reduce = "chi2"
num_dim = 500

##################### End of Initialization #####################



##################### Function Definition #####################

def clean_review(raw_review, remove_stopwords = False, output_format = "string"):
    """
    Input:
            raw_review: raw text of a movie review
            remove_stopwords: a boolean variable to indicate whether to remove stop words
            output_format: if "string", return a cleaned string 
                           if "list", a list of words extracted from cleaned string.
    Output:
            Cleaned string or list.
    """
    
    # Remove HTML markup
    text = BeautifulSoup(raw_review)
    
    # Keep only characters
    text = re.sub("[^a-zA-Z]", " ", text.get_text())
    
    # Split words and store to list
    text = text.lower().split()
    
    if remove_stopwords:
    
        # Use set as it has O(1) lookup time
        stops = set(stopwords.words("english"))
        words = [w for w in text if w not in stops]
    
    else:
        words = text
    
    # Return a cleaned string or list
    if output_format == "string":
        return " ".join(words)
        
    elif output_format == "list":
        return words
    
    
def review_to_doublelist(review, tokenizer, remove_stopwords = False):
    """
    Function which generates a list of lists of words from a review for word2vec uses.
    
    Input:
        review: raw text of a movie review
        tokenizer: tokenizer for sentence parsing
                   nltk.data.load('tokenizers/punkt/english.pickle')
        remove_stopwords: a boolean variable to indicate whether to remove stop words
    
    Output:
        A list of lists.
        The outer list consists of all sentences in a review.
        The inner list consists of all words in a sentence.
    """
    
    # Create a list of sentences
    raw_sentences = tokenizer.tokenize(review.strip())
    sentence_list = []
    
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentence_list.append(clean_review(raw_sentence, False, "list"))         
    return sentence_list


def review_to_vec(words, model, num_features):
    """
    Function which generates a feature vector for the given review.
    
    Input:
        words: a list of words extracted from a review
        model: trained word2vec model
        num_features: dimension of word2vec vectors
        
    Output:
        a numpy array representing the review
    """
    
    feature_vec = np.zeros((num_features), dtype="float32")
    word_count = 0
    
    # index2word is a list consisting of all words in the vocabulary
    # Convert list to set for speed
    index2word_set = set(model.index2word)
    
    for word in words:
        if word in index2word_set: 
            word_count += 1
            feature_vec += model[word]

    feature_vec /= word_count
    return feature_vec
    
    
def gen_review_vecs(reviews, model, num_features):
    """
    Function which generates a m-by-n numpy array from all reviews,
    where m is len(reviews), and n is num_feature
    
    Input:
            reviews: a list of lists. 
                     Inner lists are words from each review.
                     Outer lists consist of all reviews
            model: trained word2vec model
            num_feature: dimension of word2vec vectors
    Output: m-by-n numpy array, where m is len(review) and n is num_feature
    """

    curr_index = 0
    review_feature_vecs = np.zeros((len(reviews), num_features), dtype="float32")

    for review in reviews:

       if curr_index%1000 == 0.:
           print "Vectorizing review %d of %d" % (curr_index, len(reviews))
   
       review_feature_vecs[curr_index] = review_to_vec(review, model, num_features)
       curr_index += 1
       
    return review_feature_vecs
    
    
##################### End of Function Definition #####################