from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import math


TZ = pytz.timezone("Asia/Shanghai")

OUTPUT = "qingdao_bainidi.ics"


# ==========================
# 青岛潮汐模型
# ==========================

def calculate_tide():

    now = datetime.now(TZ)

    # 朔望月周期模拟
    lunar_day = now.day % 15


    if lunar_day in [0,1,14]:
        height = 0.7
        score = "⭐⭐⭐⭐⭐"

    elif lunar_day in [2,3,12,13]:
        height = 1.1
        score = "⭐⭐⭐⭐"

    else:
        height = 1.6
        score = "⭐⭐⭐"



    # 青岛半日潮近似时间
    low_hour = (
        6 + (now.day % 6)
    )


    low_time = now.replace(
        hour=low_hour,
        minute=20,
        second=0,
        microsecond=0
    )


    return {
        "time": low_time,
        "height": height,
        "score": score
    }



# ==========================
# 生成 ICS
# ==========================

def create_calendar():

    tide = calculate_tide()


    cal = Calendar()

    cal.add(
        "prodid",
        "-//Qingdao Bainidi Tide//CN"
    )

    cal.add(
        "version",
        "2.0"
    )


    cal.add(
        "X-WR-CALNAME",
        "🌊白泥地赶海"
    )



    event = Event()


    start = (
        tide["time"]
        -
        timedelta(hours=2)
    )


    end = (
        tide["time"]
        +
        timedelta(hours=1)
    )


    event.add(
        "summary",
        f"🌊赶海 {tide['score']}"
    )


    event.add(
        "dtstart",
        start
    )


    event.add(
        "dtend",
        end
    )


    event.add(
        "location",
        "青岛北站白泥地公园"
    )


    event.add(
        "description",
        f"""
地点：
青岛北站白泥地

最低潮：
{tide['time'].strftime('%H:%M')}

潮高：
{tide['height']} 米

赶海指数：
{tide['score']}

建议：
低潮前2小时到低潮后1小时
"""
    )


    cal.add_component(event)



    with open(
        OUTPUT,
        "wb"
    ) as f:

        f.write(
            cal.to_ical()
        )



if __name__ == "__main__":

    create_calendar()

    print(
        "OK: qingdao_bainidi.ics"
    )
