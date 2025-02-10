import numpy as np
import pandas as pd

from const import Column
from store import net_rate, USD_rate, EUR_rate

def normalize_df(df):
    print('Normalizing acquired data...')

    df = pd.concat([df, pd.json_normalize(df['vacancy']).rename(columns = { 'vacancy': Column.ROLE })], axis = 1)    
    df = pd.concat([df, pd.json_normalize(df['employer']).rename(columns = { 'name': Column.EMPLOYER })], axis = 1)    
    df = pd.concat([df, pd.json_normalize(df['area']).rename(columns = { 'name': Column.REGION })], axis = 1)
    df = pd.concat([df, pd.json_normalize(df['schedule']).rename(columns = { 'name': Column.SCHEDULE })], axis = 1)
    df = pd.concat([df, pd.json_normalize(df['experience']).rename(columns = { 'name': Column.EXPERIENCE})], axis = 1)    
    df['key_skills'] = df['key_skills'].apply(lambda skill_dict: ' '.join([skill['name'] for skill in skill_dict]))
    df['avg_salary'] = df['avg_salary'].apply(lambda s: {} if pd.isna(s) else s)
    df = pd.concat([df, pd.json_normalize(df['avg_salary']).rename(columns = { 'avg_salary': Column.SALARY,
                                                                                'from': Column.SALARY_FROM,
                                                                                'to': Column.SALARY_TO,
                                                                                'currency': Column.SALARY_CURRENCY,
                                                                                'gross': Column.SALARY_GROSS
                                                                              })], axis = 1)
    # calculating an average salary per each job (using min. and max. values)
    # if specified in EUR or USD it converts to a country's currency
    # if salary is gross it calculates a net wage taking a country's tax rate
    df[Column.SALARY] = (df[[Column.SALARY_FROM, Column.SALARY_TO]]
                         .mean(axis = 'columns').np.where(df[Column.SALARY_CURRENCY] == "USD",
                         df[Column.SALARY] * USD_rate,
                         df[Column.SALARY]).np.where(df[Column.SALARY_CURRENCY] == "EUR",
                         df[Column.SALARY] * EUR_rate,
                         df[Column.SALARY]).np.where(df[Column.SALARY_GROSS] == True,
                         df[Column.SALARY] * net_rate,
                         df[Column.SALARY]))    
    
    return df