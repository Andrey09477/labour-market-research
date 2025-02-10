import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import more_itertools as mit
from collections import Counter
from operator import itemgetter

from const import Column, ROLES
from store import role_nums

#region Calculating and visualizing analytical data

def run_visualization(df):
  print('Calculating and visualizing analytical data...')

  """ Regional salaries """

  # filtering null values by salaries and regions for correct analytical data calculation
  filtered_region_df = df[(df[Column.SALARY] != 0) & (df[Column.REGION] != '0')]

  # scatter plot "Salaries offered in regions"
  filtered_region_df.plot(x = Column.SALARY, y = Column.REGION, kind = 'scatter', s = 100, figsize = (10, 10))

  # mean values of regional salaries
  count_mean_values(filtered_region_df, Column.REGION, Column.SALARY)

  # median values of regional salaries
  count_median_values(filtered_region_df, Column.REGION, Column.SALARY)

  # maximum values of regional salaries
  filtered_region_df.groupby(Column.REGION)[Column.SALARY].max().sort_values()

  """ Salaries relating to professional grades """

  # filtering null values by salaries only
  filtered_salary_df = df[df[Column.SALARY] != 0]

  # plot "Scatter and average values of offered salaries relating to professional grades
  sns.catplot(x = Column.SALARY, y = Column.GRADE, kind = 'bar', data = filtered_salary_df.sort_values(Column.GRADE, ascending = False), size = 5)

  # plot "Range/scatter of offered salaries relating to professional grades
  # (the less values in single range, the thinner and lighter figure and wider dispersion)
  sns.catplot(x = Column.SALARY, y = Column.GRADE, kind='boxen', data = filtered_salary_df.sort_values(Column.GRADE, ascending = False), height = 6, aspect = 2/1)

  # mean values of salaries relating to grades
  count_mean_values(filtered_salary_df, Column.GRADE, Column.SALARY)

  # median values of salaries relating to grades
  count_median_values(filtered_salary_df, Column.GRADE, Column.SALARY)

  """ Salaries and percentage of jobs relating to required experience """

  # plot "Range/scatter of offered salaries relating to required experience"
  # (the more values in single range, the longer lines and wider dispersion)
  sns.catplot(x = Column.SALARY, y = Column.EXPERIENCE, kind = 'box', data = filtered_salary_df.sort_values(Column.EXPERIENCE), height = 5, aspect = 2/1)

  # mean values of salaries relating to required experience
  count_mean_values(filtered_salary_df, Column.EXPERIENCE, Column.SALARY)

  # median values of salaries relating to required experience
  count_median_values(filtered_salary_df, Column.EXPERIENCE, Column.SALARY)

  # plot "Percentage of offered jobs relating to required experience"
  plot_count_chart(Column.EXPERIENCE, df, 'Percentage of jobs')

  # percentage of offered jobs relating to required experience
  count_percentage(Column.EXPERIENCE, df)

  """ Salaries relating to IT professions """

  # plot "Scatter and average values of offered salaries relating to IT professions"
  sns.catplot(x = Column.SALARY, y = Column.ROLE, kind = 'bar', data = filtered_salary_df.sort_values(Column.SALARY), aspect = 2/1)

  # mean values of salaries relating to professions
  count_mean_values(filtered_salary_df, Column.ROLE, Column.SALARY)

  # median values of salaries relating to professions
  count_median_values(filtered_salary_df, Column.ROLE, Column.SALARY)

  """ Most in-demand skills relating to IT professions """

  for num in role_nums:
    role_name = ROLES[num].name
    plot_pie_chart(get_top_ten_skills(df, role_name), set_title(role_name))

  """ Salaries and percentage of jobs relating to work schedule """

  # plot "Scatter of offered salaries relating to work schedule"
  sns.catplot(x = Column.SALARY, y = Column.SCHEDULE, data = filtered_salary_df, size = 10, height = 5, aspect = 2/1)

  # plot "Percentage of offered jobs relating to work schedule"
  plot_count_chart(Column.SCHEDULE, df, 'Percentage of jobs')

  # percentage of offered jobs relating to work schedule
  count_percentage(Column.SCHEDULE, df)

  """ Salaries and number of jobs offered by employers """

  # plot "Top 10 employers offering higher salaries"
  sns.catplot(x = Column.SALARY, y = Column.EMPLOYER, kind='bar', height = 5, aspect = 2/1, data = filtered_salary_df.sort_values(Column.SALARY).tail(10))

  # plot "Top 10 employers offering more jobs"
  ax = sns.countplot(y = Column.EMPLOYER, data = df, order = pd.value_counts(df[Column.EMPLOYER]).iloc[:10].index)
  plt.xlabel('Number of jobs')

#endregion

#region Determining most in-demand skills required by employers

# getting most in-demand skills for certain profession
def get_top_ten_skills(df, role):
  df = df[df[Column.ROLE] == role]
  skills = df[Column.KEY_SKILLS].to_list()

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

  # counting duplicated skills and selecting ten most frequent ones
  return dict(sorted(dict(Counter(skills)).items(), key = lambda item: item[1], reverse = True)[:10])

# merging multiple nested lists
def merge_nested_lists(initial_list):
  return [item for nested_list in initial_list for item in nested_list]

def set_title(role):
  return f'Top 10 key skills of {role}'
  
#endregion

#region Plotting charts & counting values

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