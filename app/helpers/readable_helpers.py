def currency_readable_styled(float:float) -> tuple:
    if float<0:
        return f"-${abs(float):,.2f}", {'color':'red'}
    else:
        return f"${float:,.2f}", {'color':'green'}

def currency_readable(float:float) -> str:
    if float<0:
        return f"-${abs(float):,.2f}"
    else:
        return f"${float:,.2f}"

def ordinal(n:int) -> str:
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    return ordinal(n)

def monthly_readable(str:str) -> str:
    if str.lower() == 'end':
        return 'Last day of the month'
    else:
        return ordinal(int(str))