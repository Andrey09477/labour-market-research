import pandas as pd
import requests as req

from const import ( REQUESTS,
                    JOBS_PER_PAGE,
                    ROLES,
                  )

# selecting jobs (by specialization, country and professions) and filling a dataframe
def fill_df(spec_name, country_name, role_nums):
    jobs = []
    print('Performing requests via https://api.hh.ru...')
    spec_id = get_spec_id(spec_name)
    regions_df = get_regions(country_name)
    for role_num in role_nums:
        role = ROLES[role_num]
        print(f'Searching for jobs by profession - {role.name}')
        for region_id in [region_ids for region_ids in regions_df[Column.ID]]:
            region_name = regions_df.loc[regions_df[Column.ID] == region_id][Column.NAME].values[0]
            number_of_jobs = count_jobs(spec_id, region_id, role.search_tag)
            print(f'Found {number_of_jobs} jobs by profession {role.name} and region {region_name}')
            for page_num in range(number_of_jobs // JOBS_PER_PAGE + 1):
                found_jobs = extend_jobs(get_jobs(spec_id, region_id, role.search_tag, page_num), region_name)
                if (found_jobs is not None):
                    jobs = jobs.extend(found_jobs)
    print(f'Search completed. Total number of found jobs - {len(jobs)}')
    return pd.DataFrame(jobs)

# getting a dataframe of regions
def get_regions(country_name):
    regions_df = pd.DataFrame(req.get(REQUESTS['regions']).json())
    return pd.DataFrame(regions_df[Column.AREA][regions_df[regions_df[Column.NAME] == country_name].index.tolist()[0]])

# selecting jobs by specialization, region and role
def get_jobs(spec_id, region_id, role_tag, page_num):
    res = req.get(REQUESTS['jobs'], params = { 'search_field': Column.NAME,
                                                'specialization': spec_id,
                                                'area': region_id,
                                                'text': role_tag,
                                                'page': page_num,
                                                'per_page': JOBS_PER_PAGE,
                                             })
    if (res.status_code == 200):
        return res.json()['items']
    return None
    
# adding extended information to an each job (region, description, experience, key skills)
def extend_jobs(jobs, region_name):
    for job in jobs:
        ext_job = get_job(job[Column.ID])
        job[Column.REGION] = region_name
        job[Column.DESCRIPTION] = ext_job[Column.DESCRIPTION]
        job[Column.EXPERIENCE] = ext_job[Column.EXPERIENCE]
        job[Column.KEY_SKILLS] = ext_job[Column.KEY_SKILLS]
    return jobs
    
# counting jobs selected by specialization, region and role
def count_jobs(spec_id, region_id, role_tag):
    res = req.get(REQUESTS['jobs'], params = { 'search_field' : Column.NAME,
                                                'specialization' : spec_id,
                                                'area': region_id,
                                                'text': role_tag,
                                             })
    if (res.status_code == 200):
        return int(res.json()['found'])
    return 0

# getting a job by id
def get_job(job_id):
    res = req.get(f'{REQUESTS["jobs"]}/{str(job_id)}')
    if (res.status_code == 200):
        return res.json()
    return None

# getting a specialization id by name
def get_spec_id(spec_name):
    spec_df = pd.DataFrame(req.get(REQUESTS['spec']).json())
    return spec_df.loc[spec_name in spec_df[Column.NAME]][Column.ID].values[0]