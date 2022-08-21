def input_yn() -> str:    
    _input = input('Y/N: ')
    while _input.upper() not in ['Y','N']:
        _input = input('please enter Y/N: ')
    return _input.upper()