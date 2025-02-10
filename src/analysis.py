import numpy as np
from bs4 import BeautifulSoup
import string
import re

import nltk
nltk.download('all')
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.stem.snowball import SnowballStemmer

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import f1_score

from const import GRADES, ROLES
from store import native_lang, role_nums

#region Preliminary processing text via NLP

def process_via_NLP(text):
  print('Processing text via NLP...')

  # separating text to single words (tokenization)
  words = word_tokenize(BeautifulSoup(text, 'html.parser').get_text())
  
  # deleting stop words
  eng_stop_words = set(stopwords.words("english"))
  words = [word for word in words if word not in eng_stop_words]
  native_stop_words = set(stopwords.words(native_lang))
  words = [word for word in words if word not in native_stop_words]

  # deleting punctuation characters
  punctuations = list(string.punctuation).extend(['•', '—', '–', '«', '»', "'", '``', '“', '”', '.', '’', '·', '●'])
  words = [word for word in words if word not in punctuations]

  # stemming each word (determining word roots and slicing ends)
  words = [PorterStemmer().stem(word) for word in words]
  words = [SnowballStemmer(native_lang).stem(word) for word in words]

  return  ' '.join(words) 

#endregion

#region Determining IT professions by keywords

def get_role(job_name):
  for num in role_nums:
    role = ROLES[num]
    if (re.search(role.search_tag, job_name, re.I)):
      return role.name
    else:
      return 'undefined'

#endregion

#region Determining professional grades by keywords

def get_grade(job_name):
  for grade in GRADES:
    if (re.search(grade, job_name, re.I)):
      return grade
    else:
      return 'undefined'

#endregion

#region Determining professional grades via machine learning (classification method)

def build_learning_model(df, training_columns, fillable_column):
  print('Training a learning model based on acquired data...')

  X = df[training_columns].apply(' '.join, axis = 1)
  Y = df[fillable_column]

  train_text, test_text = train_test_split(X, test_size = 0.25, random_state = 42)  
  train_labels, test_labels = train_test_split(Y, test_size = 0.25, random_state = 42)

  word_vectorizer = CountVectorizer(min_df = 9)
  word_vectorizer.fit(X)
  train_word_features = word_vectorizer.transform(train_text)
  test_word_features = word_vectorizer.transform(test_text)

  classifier = DecisionTreeClassifier()
  classifier.fit(train_word_features, train_labels)
  pred_train = classifier.predict(train_word_features)
  pred_test = classifier.predict(test_word_features)

  train_score = f1_score(train_labels, pred_train, average = 'micro')
  train_cross_score = np.mean(cross_val_score(classifier, train_word_features, train_labels, cv = 15, scoring = 'f1_micro'))
  test_score = f1_score(test_labels, pred_test, average = 'micro')
  print('Training completed')
  print(f'Train score: {str(train_score)}')
  print(f'Train cross score: {str(train_cross_score)}')
  print(f'Test score: {str(test_score)}')

  return classifier, word_vectorizer

def fill_df_with_learned_model(classifier, word_vectorizer, df, training_columns, fillable_column):
  print(f'Filling empty cells in the {fillable_column} column with the learned model...')
  X = df[training_columns].apply(' '.join, axis = 1)
  df[fillable_column] = classifier.predict(word_vectorizer.transform(X))
  return df

#endregion