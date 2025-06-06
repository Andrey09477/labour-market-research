import numpy as np
import pandas as pd

from const import Column
from store import net_rate, USD_rate, EUR_rate

def normalize_df(df):
    print('Normalizing acquired data...')

    df = pd.concat([df, pd.json_normalize(df['vacancy']).rename(columns = { 'vacancy': Column.ROLE.value })], axis = 1)
    df = pd.concat([df, pd.json_normalize(df['employer']).rename(columns = { 'name': Column.EMPLOYER.value })], axis = 1)
    df = pd.concat([df, pd.json_normalize(df['area']).rename(columns = { 'name': Column.REGION.value })], axis = 1)
    df = pd.concat([df, pd.json_normalize(df['schedule']).rename(columns = { 'name': Column.SCHEDULE.value })], axis = 1)
    df = pd.concat([df, pd.json_normalize(df['experience']).rename(columns = { 'name': Column.EXPERIENCE.value })], axis = 1)
    df['key_skills'] = df['key_skills'].apply(lambda skill_dict: ' '.join([skill['name'] for skill in skill_dict]))
    df['avg_salary'] = df['avg_salary'].apply(lambda s: {} if pd.isna(s) else s)
    df = pd.concat([df, pd.json_normalize(df['avg_salary']).rename(columns = { 'avg_salary': Column.SALARY.value,
                                                                                'from': Column.SALARY_FROM.value,
                                                                                'to': Column.SALARY_TO.value,
                                                                                'currency': Column.SALARY_CURRENCY.value,
                                                                                'gross': Column.SALARY_GROSS.value
                                                                              })], axis = 1)
    # calculating an average salary per each job (using min. and max. values)
    # if specified in EUR or USD it converts to a country's currency
    # if salary is gross it calculates a net wage taking a country's tax rate
    df[Column.SALARY.value] = (df[[Column.SALARY_FROM.value, Column.SALARY_TO.value]]
                                  .mean(axis = 'columns').np.where(df[Column.SALARY_CURRENCY.value] == "USD",
                                df[Column.SALARY.value] * USD_rate,
                                df[Column.SALARY.value]).np.where(df[Column.SALARY_CURRENCY.value] == "EUR",
                                df[Column.SALARY.value] * EUR_rate,
                                df[Column.SALARY.value]).np.where(df[Column.SALARY_GROSS.value] == True,
                                df[Column.SALARY.value] * net_rate,
                                df[Column.SALARY.value]))
    
    return df
