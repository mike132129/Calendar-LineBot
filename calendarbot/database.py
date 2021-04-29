import os
import psycopg2
import logging
from datetime import datetime
from .utils import _parse_time

logging.basicConfig(level=logging.CRITICAL)

table_columns = '(user_id, event, event_time, event_position, note, id, create_time)'

example_query1 = '1 吃飯 1/2 17.45 潮肉東豐街 帶五百塊'
example_query2 = '2'
example_query3 = '3 1'

help_message   = "輸入指令: \n" + \
                 "0 : 幫助\n" + \
                 "1 事件 日期 時間 地點 備註: 新增事件\n" + \
                 "2 : 確認行事曆\n" +\
                 "3 事件id : 刪除事件"

insert_example = '1 吃飯 1/2 17.45 潮肉東豐街 帶五百塊 or 1 吃飯 2022/1/2 17.45 潮肉東豐街 帶五百塊'
delete_example = '3 id 是事件的編號'

def Create_Database():

    logging.debug('database testing')

    if dev_mode:
        DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a calendar-mike').read()[:-1]
    else:
        DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    # SQL_order = '''DROP TABLE [IF EXISTS] table_name [CASCADE | RESTRICT];'''
    SQL_order = '''CREATE TABLE calendar_user(
                    user_id TEXT,
                    event VARCHAR (20) NOT NULL,
                    event_time TIMESTAMP NOT NULL,
                    event_position VARCHAR (30),
                    note VARCHAR (100),
                    id VARCHAR (2),
                    create_time TIMESTAMP NOT NULL
              );'''

    cursor.execute(SQL_order)
    conn.commit()
    cursor.close()
    conn.close()

    logging.debug('Create Successfully')

    return

def Process_Query(_id, query, _dev_mode):
    global dev_mode
    dev_mode = _dev_mode
    query = query.split()

    if query[0] == '0':
        reply_message = help_message

    elif query[0] == '1':

        if len(query) == 5:
            query += ['']

        elif len(query) == 4:
            query += ['', '']
        try:
            e_time = _parse_time(query)
            logging.debug(query)
            logging.debug(e_time)

        except:
            return '請輸入正確的日期格式 EX: 2022/1/1 or 2/4\n' + \
                   '及時間格式 EX: 13:45 or 13.45'

        try:
            logging.debug('insert')
            insert_query = (_id, query[1], e_time, query[4], query[5], '0', datetime.now())
            logging.debug(insert_query)
        except:
            pass

        insert = _line_insert_event(insert_query)

        if insert:
            sorted_calendar = _get_sort_user_calendar(_id)
            reply_message   = _get_sort_calendar_text(sorted_calendar, _id, update=True)
        else:
            raise Exception('sort fail')

    elif query[0] == '2': # look up
        sorted_calendar = _get_sort_user_calendar(_id)
        reply_message   = _get_sort_calendar_text(sorted_calendar, _id)

    elif query[0] == '3': # delete
        try:
            _delete_by_event_id(_id, query[1])
            sorted_calendar = _get_sort_user_calendar(_id)
            reply_message   = _get_sort_calendar_text(sorted_calendar, _id, update=True)
        except:
            reply_message = delete_example
            raise Exception('delete fail')


    elif query[0] == 'Dev':
        logging.debug('Developement Mode')
        reply_message = show_table()
    else:
        raise Exception("cannot complete the order")

    return reply_message

def _line_insert_event(query):
    try:
        if dev_mode:
            DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a calendar-mike').read()[:-1]
        else:
            DATABASE_URL = os.environ['DATABASE_URL']

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()

        SQL_order = f'''INSERT INTO calendar_user {table_columns} VALUES (%s, %s, %s, %s, %s, %s, %s);'''

        cursor.execute(SQL_order, query)

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except:
        logging.debug('insert failed')
        return False

def _delete_by_event_id(_id, e_id):

    try:
        if dev_mode:
            DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a calendar-mike').read()[:-1]
        else:
            DATABASE_URL = os.environ['DATABASE_URL']

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        
        delete = (_id, e_id)
        SQL_order = f"DELETE FROM calendar_user WHERE (user_id=%s and id=%s)"
        
        cursor.execute(SQL_order, delete)
        conn.commit()
        cursor.close()
        conn.close()

    except:
        print('failed')

    return 'check'

def _get_sort_user_calendar(_id):
    try:
        if dev_mode:
            DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a calendar-mike').read()[:-1]
        else:
            DATABASE_URL = os.environ['DATABASE_URL']

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()

        SQL_order = "SELECT * FROM calendar_user WHERE user_id='{}' ORDER BY event_time;".format(_id)

        cursor.execute(SQL_order)
        rows = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        return rows

    except:

        logging.debug('sort query failed')
        return False

def _get_sort_calendar_text(all_calendar, _id, update=False):

    text = '=======REMINDER=======\n\n'

    if update:
        _update_event_id(all_calendar, _id)

    for i, (_id, event, time, position, note, e_id, create_time) in enumerate(all_calendar, 1):
        
        year, month, day, hour, minute, am_pm = time.strftime('%Y %m %d %I %M %p').split()
        text += str(i) + '. ' + event + '\n' + \
                len(str(i)) * ' ' + '   ' + '時間：' + (str(year) + '/' if year != datetime.now().year else '') + month + '/' + day + ' ' + hour + ':' + minute + ' ' + am_pm + '\n' + \
                len(str(i)) * ' ' + '   ' + '地點：' + position + '\n' + \
                len(str(i)) * ' ' + '   ' + '備註：' + note + '\n\n' + \
                '=======================\n\n'

    return text

def _update_event_id(all_calendar, _id):
    try:
        if dev_mode:
            DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a calendar-mike').read()[:-1]
        else:
            DATABASE_URL = os.environ['DATABASE_URL']

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        
        id_change = []
        SQL_order = f"UPDATE calendar_user SET id=%s WHERE create_time=%s"
        for i, c in enumerate(all_calendar, 1):
            id_change.append((str(i), c[-1]))
        cursor.executemany(SQL_order, id_change)
        SQL_order = 'SELECT * from calendar_user'
        cursor.execute(SQL_order)
        conn.commit()
        cursor.close()
        conn.close()

    except:
        print('failed')

    return 'check'


def show_table():
    try:
        if dev_mode:
            DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a calendar-mike').read()[:-1]
        else:
            DATABASE_URL = os.environ['DATABASE_URL']

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        SQL_order = '''SELECT * FROM calendar_user;'''
        cursor.execute(SQL_order)
        rows = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        print(rows)

    except:
        print('failed')

    return 'check'
    # cursor = conn.cursor()

    # SQL_order = '''SELECT * FROM calendar_user;'''

    # cursor.execute(SQL_order)
    # conn.commite()
    # cursor.close()
    # conn.close()

    # return

def delete_table():
    try:
        if dev_mode:
            DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a calendar-mike').read()[:-1]
        else:
            DATABASE_URL = os.environ['DATABASE_URL']

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        SQL_order = '''DROP TABLE IF EXISTS calendar_user;'''
        cursor.execute(SQL_order)
        conn.commit()
        cursor.close()
        conn.close()

    except:
        print('failed')

    return 'check'

if __name__ == '__main__':
    # Create_Database()
    # delete_table()
    pass














