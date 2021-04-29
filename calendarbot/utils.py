from datetime import datetime

def _parse_time(query):

    date = query[2].split('/')
    time = query[3].split('.') if len(query[3].split('.')) == 2 else query[3].split(':')

    if len(date) == 2:
        year  = datetime.now().year
        month = date[0]
        day   = date[1]

    elif len(date) == 3:
        year  = date[0]
        month = date[1]
        day   = date[2]

    else:
        raise Exception("請輸入正確的日期格式 EX: 2022/1/1 or 2/4")

    e_time = datetime(int(year), int(month), int(day), int(time[0]), int(time[1]))

    return e_time