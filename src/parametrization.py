from const import COUNTRIES, ROLES, ERR_MES

def select_country():
    print('Enter a country number:')
    [print(f'{i} - {country.name}') for i, country in enumerate(COUNTRIES)]
    num = 0
    try:
        num = int(input())
    except:
        print(ERR_MES)
        return select_country()
    if num > len(COUNTRIES)-1:
        print('No such country number')
        return select_country()
    return num

def get_net_rate(country_num):
    return 1-COUNTRIES[country_num].tax_rate

def get_currency_rates():
    try:
        return int(input('Enter the current USD rate for correct salary calculation: ')), int(input('Enter the current EUR rate: '))
    except:
        print(ERR_MES)
        return get_currency_rates()

def select_roles():
    print('Enter numbers of preferred professions using a separator (dot, comma or gap) or just press Enter to select all ones:')
    all_nums = []
    for i, role in enumerate(ROLES):
        all_nums.append(i)
        print(f'{str(i)} - {role.name}')
    nums = input()
    if nums == "":
        return all_nums
    else:
        selected_nums = set()
        try:
            for s in [',','.',' ']:
                if s in nums:
                    selected_nums = set(map(int, nums.split(s)))
                    break
            if len(selected_nums) == 0:
                selected_nums = set(map(int, [nums]))
        except:
            print(ERR_MES)
            return select_roles()
        for num in selected_nums:
            if num > len(ROLES)-1:
                print(f'No such profession number - {num}')
                return select_roles()
        return selected_nums