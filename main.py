import httpx
from datetime import datetime
from zhconv import convert
import time

# googletrans==4.0.0rc1
# from googletrans import Translator
# translator = Translator(service_urls=['translate.google.com'])
# print(translator.translate('Hello', dest='zh-CN').text)


# reference https://github.com/lk-itween/Calendar
def set_ics_header(year):
    return "BEGIN:VCALENDAR\n" \
        + "PRODID:NULL\n" \
        + "VERSION:2.0\n" \
        + "CALSCALE:GREGORIAN\n" \
        + "METHOD:PUBLISH\n" \
        + f"X-WR-CALNAME:{year}年-休市安排\n" \
        + "X-WR-TIMEZONE:Asia/Shanghai\n" \
        + f"X-WR-CALDESC:{year}年-休市安排\n" \
        + "BEGIN:VTIMEZONE\n" \
        + "TZID:Asia/Shanghai\n" \
        + "X-LIC-LOCATION:Asia/Shanghai\n" \
        + "BEGIN:STANDARD\n" \
        + "TZOFFSETFROM:+0800\n" \
        + "TZOFFSETTO:+0800\n" \
        + "TZNAME:CST\n" \
        + "DTSTART:19700101T000000\n" \
        + "END:STANDARD\n" \
        + "END:VTIMEZONE\n"
def set_jr_ics(date, eventsummary, eventdetail, uid):
    subscrible_url='https://raw.githubusercontent.com/gaoxx37/stockHolidayCalendar/main/ChinaHongkongUSAstockholidays.ics '
    return "BEGIN:VEVENT\n" \
        + f"DTSTART;VALUE=DATE:{date}\n" \
        + f"DTSTAMP:{date}T000001\n" \
        + f"UID:{date}T{uid:0>6}_jr\n" \
        + f"CREATED:{date}T000001\n" \
        + f"DESCRIPTION:休市原因:{eventdetail}\\n\\n日历订阅地址→{subscrible_url}\n" \
        + f"LAST-MODIFIED:{datetime.now().strftime('%Y%m%dT%H:%M:%S')}\n" \
        + "SEQUENCE:0\n" \
        + "STATUS:CONFIRMED\n" \
        + f"SUMMARY:{eventsummary}\n" \
        + "TRANSP:TRANSPARENT\n" \
        + "END:VEVENT\n"


        # + f"DTSTART;VALUE=DATE:{date}\n" \
        # 缺省DTEND字段表示全天事件，参考 https://stackoverflow.com/questions/1716237/single-day-all-day-appointments-in-ics-files
        # + f"DTEND;VALUE=DATE:{date}\n" \


if __name__ == '__main__':
    year = int(datetime.now().strftime('%Y'))
    starttime=datetime(year,1,1,0,0,0)
    endtime=datetime(year,12,31,23,59,59)
    starttime=int(time.mktime(starttime.timetuple()))
    endtime = int(time.mktime(endtime.timetuple()))

    #reference1 https://blog.51cto.com/u_15652786/5325292
    #reference2 https://www.zhihu.com/question/33872126/answer/2287006459
    url_jisilu=f'https://www.jisilu.cn/data/calendar/get_calendar_data/?qtype=OTHER&start={starttime}&end={endtime}'

    #reference1  https://blog.csdn.net/weixin_46281427/article/details/124641599
    response = httpx.get(url_jisilu)
    if response.status_code == 200:
        htmlcontent = response.text


    content=eval(htmlcontent)
    date_and_event=[(datetime.strptime(item['start'],'%Y-%m-%d %H:%M:%S').strftime('%Y%m%d'), \
                     item['title'], convert(item['description'], 'zh-cn')) for item in content]

    date_and_event.sort(key=lambda x: x[0])
    date_and_event_uid = date_and_event
    pre_num = 0
    for num in range(len(date_and_event_uid)):
        if date_and_event_uid[num][0] != date_and_event_uid[pre_num][0]:
            pre_num = num
        date_and_event_uid[num] += (num - pre_num + 1,)
    event_ics = ''.join(
        map(lambda x: set_jr_ics(*x), date_and_event_uid))

    header = set_ics_header(year)
    full_ics = header + event_ics + 'END:VCALENDAR'
    fname = str(year) + '_ChinaHongkongUSAstockholidays.ics'
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(full_ics)

    with open('ChinaHongkongUSAstockholidays.ics', 'w', encoding='utf-8') as f:
        f.write(full_ics)

    
    #每年12月31日定时爬取下一年的休市安排 https://blog.csdn.net/u010214511/article/details/127079323
    # https://xiaoshen.blog.csdn.net/article/details/127890033?spm=1001.2101.3001.6650.1&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-1-127890033-blog-125866755.235%5Ev28%5Epc_relevant_default_base1&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-1-127890033-blog-125866755.235%5Ev28%5Epc_relevant_default_base1&utm_relevant_index=2
