""" Analysis of conditions and qualification requirements within IT labour market """

#region Common data

from enum import Enum
import pandas as pd
import numpy as np

class column(Enum):
  vacancy = 'vacancy'
  profession = 'profession'
  grade = 'grade'
  key_skills = 'key_skills'
  experience = 'experience'
  salary = 'avg_salary'
  schedule = 'schedule'
  region = 'region'
  employer = 'employer'

class role(Enum):
  QA_engineer = 'QA engineer'
  analyst = 'Analyst'
  data_engineer = 'Data engineer'
  sys_admin = 'System administrator'
  security_specialist = 'Information security specialist'
  devops_engineer = 'DevOps engineer'
  frontend_developer = 'Frontend developer'
  backend_developer = 'Backend developer'
  fullstack_developer = 'Fullstack developer'

#endregion


#region Preparing the dataset

# loading the dataset from a CSV-file
import tkinter.filedialog as fd
jobs_df = pd.read_csv(fd.askopenfilename(), sep=',')

# deleting extra columns, replacing NaN values to 0 and setting column types to exclude errors during analysis
jobs_df = jobs_df.drop('Unnamed: 0', 1).fillna(0).astype({ column.salary:'int64', column.vacancy:'string', column.key_skills:'string' })

#endregion


#region Preliminary processing text via NLP

import nltk
nltk.download('all')
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from bs4 import BeautifulSoup
import string

jobs_df[column.vacancy] = jobs_df[column.vacancy].apply(process_text)
jobs_df[column.key_skills] = jobs_df[column.key_skills].apply(process_text)
jobs_df[column.experience] = jobs_df[column.experience].apply(process_text)

def process_text(text):
  text = BeautifulSoup(text, 'html.parser').get_text()

  # separating text to single words (tokenization)
  words = word_tokenize(text)
  
  # deleting stop words
  eng_stop_words = set(stopwords.words("english"))
  words = [word for word in words if word not in eng_stop_words]
  ru_stop_words = set(stopwords.words("russian"))
  words = [word for word in words if word not in ru_stop_words]

  # deleting punctuation characters
  punctuations = list(string.punctuation).extend(['•', '—', '–', '«', '»', "'", '``', '“', '”', '.', '’', '·', '●'])
  words = [word for word in words if word not in punctuations]

  # stemming each word (determining roots of words and slicing ends)
  en_stemmer = PorterStemmer()
  words = [stemmer_en.stem(word) for word in words]
  ru_stemmer = SnowballStemmer("russian")
  words = [stemmer_ru.stem(word) for word in words]

  return  ' '.join(words) 

#endregion


#region Determining professional grades by keywords

import re

jobs_df[column.grade] = jobs_df[column.vacancy].apply(get_grade)

def get_grade(job_name):
  if (re.search('младший' or 'junior', job_name, re.I)):
    return 'junior'
  if (re.search('старший' or 'middle', job_name, re.I)):
    return 'middle'
  if (re.search('ведущий' or 'senior', job_name, re.I)):
    return 'senior'
  if (re.search('главный' or 'principal', job_name, re.I)):
    return 'principal'
  if (re.search('руководитель' or 'lead', job_name, re.I)):
    return 'team_lead'
  if (re.search('архитектор' or 'architect', job_name, re.I)):
    return 'architect'
  else
    return 'undefined'

#endregion


#region Determining professional grades via machine learning (classification method)

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import f1_score

# separating the dataframe to defined and undefined grades for further analysis
defined_grades_df = jobs_df[jobs_df[column.grade] != 'undefined']
undefined_grades_df = jobs_df[jobs_df[column.grade] == 'undefined']

# learning regularities and building the learning model based on defined grades and acquired data ('vacancy', 'experience', 'key_skills' columns)
classifier, word_vectorizer = build_learning_model(defined_grades_df, 
                                                   [column.vacancy, column.experience, column.key_skills], 
                                                   column.grade
                                                  )
# applying the learned model to "undefined grades" dataframe and filling 'grade' column
emulated_grades_df = fill_df_with_learned_model(classifier, 
                                                word_vectorizer, 
                                                undefined_grades_df, 
                                                [column.vacancy, column.experience, column.key_skills], 
                                                column.grade
                                               )
# getting the full graded dataframe
jobs_df = pd.concat([defined_grades_df, emulated_grades_df])

# building a learning model based on acquired data
def build_learning_model(df, training_columns, fillable_column):
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

  training_score = f1_score(train_labels, pred_train, average = 'micro')
  training_cross_score = np.mean(cross_val_score(classifier, train_word_features, train_labels, cv = 15, scoring = 'f1_micro'))
  test_score = f1_score(test_labels, pred_test, average = 'micro')
  print('training_score = ' + str(training_score))
  print('training_cross_score = ' + str(training_cross_score))
  print('test_score = ' + str(test_score))

  return classifier, word_vectorizer

# applying a learned model to a dataframe and filling a target column
def fill_df_with_learned_model(classifier, word_vectorizer, df, training_columns, fillable_column)
  X = undefined_grades_df[training_columns].apply(' '.join, axis = 1)
  df[fillable_column] = classifier.predict(word_vectorizer.transform(X))
  return df

#endregion


#region Determining IT professions by keywords

jobs_df[column.profession] = jobs_df[column.vacancy].apply(get_professions)

def get_professions(job_name):
  if (re.search('тестиров' or 'qa' and 'engineer', job_name, re.I)):
    return role.QA_engineer
  if (re.search('аналитик' or 'analyst', job_name, re.I)):
    return role.analyst
  if (re.search(('data' or 'ML' or 'AI') and 'engineer', job_name, re.I)):
    return role.data_engineer
  if (re.search('системн' and 'администр' or 'system' and 'administrator', job_name, re.I)):
    return role.sys_admin
  if (re.search('информац' and 'безопасност' or 'information' and 'security', job_name, re.I)):
    return role.security_specialist
  if (re.search('devops', job_name_name, re.I)):
    return role.devops_engineer
  if (re.search('front', job_name, re.I)):
    return role.frontend_developer
  if (re.search('back', job_name, re.I)):
    return role.backend_developer
  if (re.search('full', job_name, re.I)):
    return role.fullstack_developer
  else:
    return 'undefined'

#endregion


#region Determining most in-demand skills required by employers

import more_itertools as mit
from collections import Counter
from operator import itemgetter

# getting most in-demand skills for certain profession
def get_top_ten_skills(df, profession):
  df = df[df[column.profession] == profession]
  skills = df[column.key_skills].to_list()

  # getting a list of abbreviations
  tokenized_skills = [word_tokenize(skill) for skill in skills]
  abbrs = []
  for skill in merge_nested_lists(tokenized_skills):
    if re.match(r'^[A-Z]*(?:_[A-Z]*)*$', skill):
      abbrs.append(skill)

  # getting a list of word collocations
  all_phrases = []
  for skill in skills:
    all_phrases.append(["".join(item) for item in mit.split_before(skill, pred = lambda skill: skill.isupper())])
  phrases = []
  for phrase in merge_nested_lists(all_phrases):
    if len(phrase) > 2:
      phrases.append(phrase.rstrip())

  skills = abbrs + phrases

  # counting number of duplicated skills and returning ten most frequent ones
  return dict(sorted(dict(Counter(skills)).items(), key = lambda item: item[1], reverse = True)[:10])

# merging multiple nested lists
def merge_nested_lists(initial_list):
  return [item for nested_list in initial_list for item in nested_list]
  
#endregion


#region IT labour market insights
# * all salaries are specified in russian rubles (RUR)

import seaborn as sns
import matplotlib.pyplot as plt


""" Regional salaries* """

# filtering null values by salaries and regions for correct calculating statistical data
filtered_region_df = jobs_df[(jobs_df[column.salary] != 0) & (jobs_df[column.region] != '0')]

# scatter plot "Salaries offered in regions"
filtered_region_df.plot(x = column.salary, y = column.region, kind = 'scatter', s = 100, figsize = (10, 10))

# mean values of regional salaries
count_mean_values(filtered_region_df, column.region, column.salary)

# median values of regional salaries
count_median_values(filtered_region_df, column.region, column.salary)

# maximum values of regional salaries
filtered_region_df.groupby(column.region)[column.salary].max().sort_values()


""" Salaries* relating to professional grades """

# filtering null values by salaries only
filtered_salary_df = jobs_df[jobs_df[column.salary] != 0]

# plot "Scatter and average values of offered salaries relating to professional grades
sns.catplot(x = column.salary, y = column.grade, kind = 'bar', data = filtered_salary_df.sort_values(column.grade, ascending = False), size = 5)

# plot "Range/scatter of offered salaries relating to professional grades 
# (the less values in single range, the thinner and lighter figure and wider dispersion
sns.catplot(x = column.salary, y = column.grade, kind='boxen', data = filtered_salary_df.sort_values(column.grade, ascending = False), height = 6, aspect = 2/1)

# mean values of salaries relating to grades
count_mean_values(filtered_salary_df, column.grade, column.salary)

# median values of salaries relating to grades
count_median_values(filtered_salary_df, column.grade, column.salary)


""" Salaries* and percentage of jobs relating to required experience """

# plot "Range/scatter of offered salaries relating to required experience 
# (the more values in single range, the longer lines and wider dispersion
sns.catplot(x = column.salary, y = column.experience, kind = 'box', data = filtered_salary_df.sort_values(column.experience), height = 5, aspect = 2/1)

# mean values of salaries relating to required experience
count_mean_values(filtered_salary_df, column.experience, column.salary)

# median values of salaries relating to required experience
count_median_values(filtered_salary_df, column.experience, column.salary)

# plot "Percentage of offered jobs relating to required experience
plot_count_chart(column.experience, jobs_df, 'Percentage of jobs')

# percentage of offered jobs relating to required experience
count_percentage(column.experience, jobs_df)


""" Salaries* relating to IT professions """

# plot "Scatter and average values of offered salaries relating to IT professions
sns.catplot(x = column.salary, y = column.profession, kind = 'bar', data = filtered_salary_df.sort_values(column.salary), aspect = 2/1)

# mean values of salaries relating to professions
count_mean_values(filtered_salary_df, column.profession, column.salary)

# median values of salaries relating to professions
count_median_values(filtered_salary_df, column.profession, column.salary)


""" Most in-demand skills relating to IT professions """

# Ten key skills of DevOps engineer
plot_pie_chart(get_top_ten_skills(jobs_df, role.devops_engineer), set_title(role.devops_engineer))

# Ten key skills of Fullstack developer
plot_pie_chart(get_top_ten_skills(jobs_df, role.data_engineer), set_title(role.data_engineer))

# Ten key skills of Fullstack developer
plot_pie_chart(get_top_ten_skills(jobs_df, role.fullstack_developer), set_title(role.fullstack_developer))

# Ten key skills of Backend developer
plot_pie_chart(get_top_ten_skills(jobs_df, role.backend_developer), set_title(role.backend_developer))

# Ten key skills of Frontend developer
plot_pie_chart(get_top_ten_skills(jobs_df, role.frontend_developer), set_title(role.frontend_developer))

def set_title(profession):
  return 'Top 10 key skills of ' + profession


""" Salaries* and percentage of jobs relating to work schedule """

# plot "Scatter of offered salaries relating to work schedule
sns.catplot(x = column.salary, y = column.schedule, data = filtered_salary_df, size = 10, height = 5, aspect = 2/1)

# plot "Percentage of offered jobs relating to work schedule
plot_count_chart(column.schedule, jobs_df, 'Percentage of jobs')

# percentage of offered jobs relating to work schedule
count_percentage(column.schedule, jobs_df)


""" Salaries* and number of jobs offered by employers """

# plot "Top 10 employers offering higher salaries
sns.catplot(x = column.salary, y = column.employer, kind='bar', height = 5, aspect = 2/1, data = filtered_salary_df.sort_values(column.salary).tail(10))

# plot "Top 10 employers offering more jobs
ax = sns.countplot(y = column.employer, data = jobs_df, order = pd.value_counts(jobs_df[column.employer]).iloc[:10].index)
plt.xlabel('Number of jobs')


###

# plotting a pie chart
def plot_pie_chart(val_dict, title):
  fig1, ax1 = plt.subplots(figsize = (7, 7))
  ax1.axis('equal')
  ax1.pie(list(val_dict.values()), labels = list(val_dict.keys()), autopct = '%1.2f%%')
  plt.title(title)
  plt.show()

# plotting percentage of values by any criteria
def plot_count_chart(countable_col, df, label):
  ax = sns.countplot(y = countable_col, data = df)
  plt.xlabel(label)
  ax.set_xticklabels(map('{:.0f}%'.format, 100 * ax.xaxis.get_majorticklocs() / len(df[countable_col])))

# counting percentage of values by any criteria
def count_percentage(countable_col, df):
  return (df.groupby([countable_col])[countable_col].count() * 100 / len(df)).round(1).sort_values()

# counting mean values
def count_mean_values(df, grouping_col, countable_col):
  return df.groupby(grouping_col)[countable_col].mean().round(0).sort_values()

# counting median values
def count_median_values(df, grouping_col, countable_col):
  return df.groupby(grouping_col)[countable_col].median().round(0).sort_values()

#endregion
