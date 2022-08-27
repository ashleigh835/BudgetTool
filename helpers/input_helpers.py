def enum_ls(ls) -> list:
    return dict((i,j) for i,j in enumerate(ls))  

def input_yn() -> str:    
    _input = input('Y/N: ')
    while _input.upper() not in ['Y','N']:
        _input = input('please enter Y/N: ')
    return _input.upper()

def determine_from_ls(ls, string='an option', labels=[]) -> str:
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

def determine_amount(string='an amount') -> float:
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