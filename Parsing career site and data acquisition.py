""" Parsing the career site (hh.ru) and data acquisition via api.hh.ru
(for further analysis of conditions and qualification requirements within IT labour market) """

#region Common data

import pandas as pd
import numpy as np

class column(Enum):
    id = 'id'
    city_id = 'city_id'
    schedule_id = 'schedule_id'
    experience_id = 'experience_id'
    name = 'name'
    vacancy = 'vacancy'
    grade = 'grade'
    description = 'description'
    key_skills = 'key_skills'
    experience = 'experience'
    avg_salary = 'avg_salary'
    salary_currency = 'salary_currency'
    salary_gross = 'salary_gross'
    salary_from = 'salary_from'
    salary_to = 'salary_to'
    schedule = 'schedule'
    region = 'region'
    city = 'city'
    area = 'area'
    employer = 'employer'

country = 'Россия'
spec = "информационные технологии"
roles = ['backend', 'frontend',  'fullstack', 'devops', 'qa', 'analyst', 'data engineer,', 'scientist', 'administrator', 'security']

#endregion


#region Parameters of downloading data via the site API

import requests

areas_request = 'https://api.hh.ru/areas'
jobs_request = 'https://api.hh.ru/vacancies'
spec_request = 'https://api.hh.ru/specializations'
jobs_per_page = 100

# endregion


#region Parsing the site (by roles), data acquisition and filling the dataframe

jobs_df = fill_jobs_df(country, spec, roles)

# selecting jobs and filling a dataframe
def fill_jobs_df(country, spec, roles):
    jobs = []
    spec_id = get_spec_id(spec)
    regions_df = get_regions(country)
    for role in roles:        
        print('Searching jobs by role - ' + role)
        for region_id in [i for i in regions_df[column.id]]:
            number_of_jobs = count_jobs(role, region_id, spec_id)
            region_name = regions_df.loc[regions_df[column.id] == region_id][column.name].values[0]
            print('Current region - ' + region_name)
            for page in range(number_of_jobs // jobs_per_page + 1):
                found_jobs = extend_jobs(get_jobs(role, region_id, spec_id, page), region_name)
                if (found_jobs is not None):
                    jobs = jobs.extend(found_jobs)
    print('Search complete. Found ' + len(jobs) + ' jobs')
    return pd.DataFrame(jobs)

# getting a dataframe of regions
def get_regions(country):
    regions_df = pd.DataFrame(requests.get(areas_request).json())
    return pd.DataFrame(regions_df[column.area][regions_df[regions_df[column.name] == country].index.tolist()[0]])

# getting a list of jobs selected by specialization id, region and role
def get_jobs(role, region_id, spec_id, page):
    res = requests.get(jobs_request, params = { 'text': role,
                                                'search_field': column.name,
                                                'area': region_id,
                                                'specialization': spec_id
                                                'page': page,
                                                'per_page': jobs_per_page,
                                              })
    if (res.status_code == 200):
        return res.json()['items']
    return None
    
# adding extended information to each job (region, description, experience, key skills)
def extend_jobs(jobs, region):
    for job in jobs:
        ext_job = get_job(job[column.id])
        job[column.description] = ext_job[column.description]
        job[column.experience] = ext_job[column.experience]
        job[column.key_skills] = ext_job[column.key_skills]    
        job[column.region] = region
    return jobs
    
# counting jobs selected by specialization id, region and role
def count_jobs(role, region_id, spec_id):
    res = requests.get(jobs_request, 
                          params = { 'text': role,
                                     'per_page' : 1,
                                     'search_field' : column.name,
                                     'area': region_id,
                                     'specialization' : spec_id
                                   })
    if (res.status_code == 200):
        return int(res.json()['found'])
    return 0

# getting a job by id
def get_job(job_id):
    res = requests.get(jobs_request + "/" + str(job_id))
    if (res.status_code == 200):
        return res.json()
    return None

# getting a specialization id by name
def get_spec_id(spec_name):
    spec_df = pd.DataFrame(requests.get(spec_request).json())
    return spec_df.loc[spec_name in spec_df[column.name]][column.id].values[0]

#endregion


#region Data normalization (for further analysis)

USD_rate = 90
EUR_rate = 100
net_wage_rate = 0.87 # (-13% (tax))

# normalizing the dataframe content
jobs_df = normalize_jobs_df(jobs_df)

def normalize_jobs_df(jobs_df):
    
    # normalizing data in the column "employer"
    employer_col = pd.json_normalize(jobs_df[column.employer]).rename(columns = { 'name': column.employer })
    normalized_df = pd.concat([jobs_df, employer_col], axis = 1)
    
    # normalizing data in the column "area"
    city_col = pd.json_normalize(normalized_df[column.area]).rename(columns = { 'id': column.city_id, 'name': column.city })
    normalized_df = pd.concat([normalized_df, city_col], axis = 1)

    # normalizing data in the column "schedule"
    schedule_col = pd.json_normalize(normalized_df[column.schedule]).rename(columns = { 'id': column.schedule_id, 'name': column.schedule })
    normalized_df = pd.concat([normalized_df, schedule_col], axis = 1)

    # normalizing data in the column "experience"
    experience_col = pd.json_normalize(normalized_df[column.experience]).rename(columns = { 'id': column.experience_id, 'name': column.experience})
    normalized_df = pd.concat([normalized_df, experience_col], axis = 1)
    
    # normalizing data in the column "skills"
    normalized_df[column.key_skills] = normalized_df[column.key_skills].apply(lambda skill_dict: ' '.join([skill[column.name] for skill in skill_dict]))

    # normalizing data in the column "salary"
    normalized_df[column.avg_salary] = normalized_df[column.avg_salary].apply(lambda x: {} if pd.isna(x) else x)
    salary_col = pd.json_normalize(normalized_df[column.avg_salary]).rename(columns = { 'from': column.salary_from,
                                                                                        'to': column.salary_to, 
                                                                                        'currency': column.salary_currency,
                                                                                        'gross': column.salary_gross
                                                                                      })
    normalized_df = pd.concat([normalized_df, salary_col], axis = 1)
    
    # calculating an average salary per each job (using min. and max. values)
    # if specified at EUR or USD it converts to RUR
    # if salary is gross it calculates taking a tax rate
    normalized_df[column.avg_salary] = normalized_df[[column.salary_from, column.salary_to]].mean(axis = 'columns')
                                    .np.where(normalized_df[column.salary_currency] == "USD",
                                              normalized_df[column.avg_salary] * USD_rate,
                                              normalized_df[column.avg_salary])
                                    .np.where(normalized_df[column.salary_currency] == "EUR",
                                              normalized_df[column.avg_salary] * EUR_rate,
                                              normalized_df[column.avg_salary])
                                    .np.where(normalized_df[column.salary_gross] == True, 
                                              normalized_df[column.avg_salary] * net_wage_rate,
                                              normalized_df[column.avg_salary])
    
    return normalized_df

#endregion


#region Saving the final dataframe to CSV-file

# selecting crucial columns
jobs_df = jobs_df[[ column.id, 
                    column.vacancy,
                    column.description,
                    column.key_skills, 
                    column.experience,
                    column.employer,
                    column.region, 
                    column.city,
                    column.schedule, 
                    column.avg_salary, 
                  ]]

import csv
jobs_df.to_csv('jobs_dataset.csv', index = False, header = True, sep=',')

#endregion