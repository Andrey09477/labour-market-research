import csv
import pandas as pd
import tkinter.filedialog as fd

from const import Column, ERR_MES, COUNTRIES, SPEC_NAME
import store
from parametrization import select_country, select_roles, get_net_rate, get_currency_rates
from acquisition import fill_df
from normalization import normalize_df
from analysis import process_via_NLP, build_learning_model, fill_df_with_learned_model, get_grade, get_role
from visualization import run_visualization

''' Parsing the career site (www.hh.ru) via public API, selecting jobs
        and analysis of conditions and qualification requirements within IT labour market '''

def acquire_data(spec_name, country_name, role_nums):

    ''' Data acquisition and filling the dataframe '''

    df = fill_df(spec_name, country_name, role_nums)

    ''' Normalizing acquired data '''

    df = normalize_df(df)

    ''' Saving the final dataframe to CSV-file '''

    # selecting the crucial columns
    df = df[[   Column.ID,
                Column.ROLE,
                Column.DESCRIPTION,
                Column.KEY_SKILLS, 
                Column.EXPERIENCE,
                Column.SALARY,
                Column.SCHEDULE,
                Column.REGION,
                Column.EMPLOYER,
            ]]
    df.to_csv(f'{input("Enter a dataframe name to save")}.csv', index = False, header = True, sep=',')

    return df

def run_analysis(df):

    # deleting extra columns, replacing NaN values to 0 and setting column data types to exclude errors during analysis
    df = df.drop('Unnamed: 0', 1).fillna(0).astype({ Column.SALARY:'int64', Column.ROLE:'string', Column.KEY_SKILLS:'string' })

    ''' Data analysis '''

    # preliminary processing text via NLP
    df[Column.ROLE] = df[Column.ROLE].apply(process_via_NLP)
    df[Column.KEY_SKILLS] = df[Column.KEY_SKILLS].apply(process_via_NLP)
    df[Column.EXPERIENCE] = df[Column.EXPERIENCE].apply(process_via_NLP)

    # determining IT professions by keywords
    df[Column.ROLE] = df[Column.ROLE].apply(get_role)

    # determining professional grades by keywords
    df[Column.GRADE] = df[Column.ROLE].apply(get_grade)

    #region Determining professional grades via machine learning (classification method)

    # separating the dataframe to defined and undefined grades for further analysis
    defined_grades_df = df[df[Column.GRADE] != 'undefined']
    undefined_grades_df = df[df[Column.GRADE] == 'undefined']

    # learning regularities and building the learning model based on previously defined grades and acquired data -
    # ('role', 'experience', 'key_skills' columns)
    classifier, word_vectorizer = build_learning_model(defined_grades_df,
                                                        [Column.ROLE, Column.EXPERIENCE, Column.KEY_SKILLS],
                                                        Column.GRADE
                                                      )

    # applying the learned model to "undefined grades" dataframe and filling the 'grade' column
    emulated_grades_df = fill_df_with_learned_model(classifier,
                                                    word_vectorizer,
                                                    undefined_grades_df,
                                                    [Column.ROLE, Column.EXPERIENCE, Column.KEY_SKILLS], 
                                                    Column.GRADE
                                                   )
    # getting the full graded dataframe
    df = pd.concat([defined_grades_df, emulated_grades_df])

    #endregion

    ''' Data visualization '''

    run_visualization(df)

def main():
    store.country_num = select_country()
    store.native_lang = COUNTRIES[store.country_num].lang
    store.role_nums = select_roles()
    num = input('''Choose one of the following analysis options (enter a number):
                    1. acquire new data from www.hh.ru, save and perform analysis
                    2. perform analysis of saved dataframe
                ''')
    if num == '1':
        store.net_rate = get_net_rate(store.country_num)
        (store.USD_rate, store.EUR_rate) = get_currency_rates()
        df = acquire_data(SPEC_NAME, COUNTRIES[store.country_num].search_tag, store.role_nums)
    elif num == '2':
        print('Select a CSV-file')
        df = pd.read_csv(fd.askopenfilename(), sep=',')
    else:
        print(ERR_MES)
        main()
    run_analysis(df)

if __name__ == "__main__":
    main()