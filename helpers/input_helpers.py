from helpers.date_helpers import weekdays
from datetime import datetime

def enum_ls(ls:list) -> list:
    return dict((i,j) for i,j in enumerate(ls))  

def input_yn() -> str:    
    _input = input('Y/N: ')
    while _input.upper() not in ['Y','N']:
        _input = input('please enter Y/N: ')
    return _input.upper()

def determine_from_ls(ls:list, string:str='an option', labels:list=[]) -> str:
    if not labels:
        labels = ls
    dct = enum_ls(ls)
    lbl_dct = enum_ls(labels)
    print(f'please choose {string} using a number listed below:')
    for indx in lbl_dct.keys(): print(f'{indx}: {lbl_dct[indx]}')
    choose_input = input('please enter an index from above: ')
    while choose_input.lower() not in [str(indx) for indx in lbl_dct.keys()]:
        choose_input = input(f'please enter an index from above: ')     
    return dct[int(choose_input)]

def determine_from_range(lower:int, upper:int, additional_options:list = [], string:str = 'an option') -> str:

    print(f"please choose {string} from the following:")
    print(f"{lower}-{upper}: enter index within the range")

    rng_ls = [i for i in range(lower,upper+1)]
    rng_option_ls = [str(indx) for indx in rng_ls]

    lbl_dct = enum_ls(additional_options)
    for indx in lbl_dct.keys(): 
        print(f'{indx+upper+1}: {lbl_dct[indx]}')
        
    additional_option_ls = [str(indx+upper+1) for indx in lbl_dct.keys()]
    option_ls = rng_option_ls + additional_option_ls

    choose_input = input('please enter an index from above: ')
    while choose_input.lower() not in option_ls:
        choose_input = input(f'please enter an index from above: ')

    if choose_input in additional_option_ls:
        return lbl_dct[int(choose_input)-upper-1]
    elif choose_input in rng_option_ls:
        return choose_input

def determine_amount(string:str='an amount') -> float:
    print(f'please input {string}')
    good_float = False
    e_enthusiasm = ''
    e_counter = 0
    while not good_float:
        amt_input = input('amount: ')
        try :
            amt_float = float(amt_input)
            good_float = True
        except ValueError:
            e_counter+=1
            if e_counter>4:
                print("We both know that that's not a string now don't we... try again"+e_enthusiasm)
                e_enthusiasm = e_enthusiasm + '!'
        except Exception as e:
            print(f'No idea what went wrong there.\n {type(e)}: {e}')
    return amt_float

def determine_weekday() -> int:
    return determine_from_ls(weekdays(), string='a weekday')

def determine_day_of_month(additional_options:list = []) -> str:
    return determine_from_range(1,31,additional_options)

def determine_date() -> datetime.date:
    print('please input a date in the format of YYYY-MM-DD')
    good_date = False
    e_enthusiasm = ''
    e_counter = 0
    while not good_date:
        date_input = input('YYYY-MM-DD: ')
        try:
            dte = datetime.strptime(date_input,'%Y-%m-%d')
            good_date = True
        except ValueError:
            e_counter+=1
            if e_counter>4:
                print("We both know that that's not a date now don't we... try again"+e_enthusiasm)
                e_enthusiasm = e_enthusiasm + '!'
        except Exception as e:
            print(f'No idea what went wrong there.\n {type(e)}: {e}')
    return dte.date()

def determine_operation_from_dict(operations:dict) -> None:  
    finished:bool = False

    while not finished:
        print()
        choice = determine_from_ls(operations.values(), labels=operations.keys())

        if choice['function'] == 'Exit':
            finished = True
        else:
            fn = choice['function']
            if not choice['vars']: 
                fn()
            else: 
                fn(**choice['vars'])

def parse_readable(name, val) -> list:
    print_ls = []
    if type(val) == str:
        print_ls += [f'{name} : {val}']
    elif type(val) == list:      
        print_ls += ['', name+':']
        for l in val:
            print_ls += ['-'*20]      
            print_ls += parse_readable(name, l)
    elif type(val) == dict:
        for l in val.keys():
            print_ls += parse_readable(l, val[l])
    return print_ls

def view_readable(read_item, name:str='') -> None:
    print_ls = ['','-'*40]
    print_ls += parse_readable(name, read_item)
    print_ls += ['-'*40]
    for p in print_ls: print(p)