from enum import Enum

class Column(Enum):
    ID = 'id'
    NAME = 'name'
    DESCRIPTION = 'description'
    KEY_SKILLS = 'key_skills'
    EXPERIENCE = 'experience'
    GRADE = 'grade'
    SALARY = 'salary'
    AVG_SALARY = 'avg_salary'
    SALARY_CURRENCY = 'salary_currency'
    SALARY_GROSS = 'salary_gross'
    SALARY_FROM = 'salary_from'
    SALARY_TO = 'salary_to'
    SCHEDULE = 'schedule'
    REGION = 'region'
    AREA = 'area'
    EMPLOYER = 'employer'

class Country:
    def __init__(self, **attrs):
        self.name = attrs['name']
        self.lang = attrs['lang']
        self.tax_rate = attrs['tax_rate']
        self.search_tag = attrs['search_tag']

class Role:
    def __init__(self, **attrs):
        self.name = attrs['name']
        self.search_tag = attrs['search_tag']

REQUESTS = {
    'spec':'https://api.hh.ru/specializations',
    'regions':'https://api.hh.ru/areas',
    'jobs':'https://api.hh.ru/vacancies',
}
JOBS_PER_PAGE = 100

COUNTRIES = (
    Country(name='Russia', lang='russian', tax_rate=0.13, search_tag='Россия'),
    Country(name='Belarus', lang='belarusian', tax_rate=0.13, search_tag='Беларусь'),
    Country(name='Kazakhstan', lang='kazakh', tax_rate=0.1, search_tag='Казахстан'),
    Country(name='Uzbekistan', lang='uzbek', tax_rate=0.12, search_tag='Узбекистан'),
    Country(name='Kyrgyzstan', lang='kyrgyz', tax_rate=0.1, search_tag='Кыргызстан'),
    Country(name='Azerbaijan', lang='azerbaijani', tax_rate=0.14, search_tag='Азербайджан'),
    Country(name='Georgia', lang='georgian', tax_rate=0.2, search_tag='Грузия'),
)

ROLES = (
   Role(name='Backend developer', search_tag='back end'),
   Role(name='Frontend developer', search_tag='front end'),
   Role(name='Fullstack developer', search_tag='full stack'),
   Role(name='Embedded developer', search_tag='embedded'),
   Role(name='iOS developer', search_tag='ios'),
   Role(name='Android developer', search_tag='android'),
   Role(name='Data analyst', search_tag='data analyst'),
   Role(name='Data engineer', search_tag='data engineer'),
   Role(name='Data scientist', search_tag='scientist'),
   Role(name='QA engineer', search_tag='qa'),
   Role(name='DevOps engineer', search_tag='dev ops'),
   Role(name='System administrator', search_tag='sys admin'),
   Role(name='Information security specialist', search_tag='info security'),
)

GRADES = ('entry', 'junior', 'middle', 'senior', 'principal', 'team lead', 'architect')

SPEC_NAME = 'информационные технологии'

ERR_MES = 'Incorrect value'