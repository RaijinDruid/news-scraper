from datetime import datetime
from flask import abort

def within_date_range(article_date, start_date, end_date):
    #if article date doesn't exist then return False as default
    if not article_date: return False

    #convert start_date to datetime objects from Str input, if start date not supplied default to min/max date for start_date, end_date respectively
    sd = datetime.strptime(start_date, "%Y-%m-%d") if type(start_date) == str else datetime.min
    ed = datetime.strptime(end_date, "%Y-%m-%d") if type(end_date) == str else datetime.max

    return sd <= article_date <= ed


def format_date(date, to_datetime=False, current_format='%d-%m-%Y', req_format="%Y-%m-%d"):
    if not date: return None
    try:
        d = datetime.strptime(date, current_format)
        if to_datetime:
            return d
        return d.strftime(req_format)
    except ValueError:
        pass
    abort(400, 'Supply a date with one of the following formats "dd-mm-yyyy"')  
