from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup
import re


# =========================
# 青岛北站白泥地赶海日历
# =========================


TZ = pytz.timezone("Asia/Shanghai")


ICS_FILE = "qingdao_bainidi.ics"


def get_tide():

    """
    获取青岛潮汐
    """

    url = "https://www.gjk.cn/tides/show-ODg4OGVi"

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }


    r = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    r.encoding = "utf-8"


    text = r.text


    # 找潮汐时间
    times = re.findall(
        r'\d{2}:\d{2}',
        text
    )


    # 找潮高 cm
    heights = re.findall(
        r'(\d{2,3})\s*cm',
        text
    )


    if len(times) < 4:

        raise Exception(
            "潮汐数据读取失败"
        )


    if len(heights) < 4:

        raise Exception(
            "潮高读取失败"
        )


    tide = []


    for i in range(4):

        tide.append(
            {
                "time":times[i],
                "height":int(heights[i])
            }
        )


    # 取两个低潮
    low = sorted(
        tide,
        key=lambda x:x["height"]
    )[0]


    return low



def level(height):

    """
    赶海指数
    """

    if height <= 100:
        return "⭐⭐⭐⭐⭐"

    elif height <=150:
        return "⭐⭐⭐⭐"

    elif height <=200:
        return "⭐⭐⭐"

    else:
        return "⭐⭐"



def create_calendar():


    tide = get_tide()


    now = datetime.now(TZ)


    hh,mm = map(
        int,
        tide["time"].split(":")
    )


    low_time = now.replace(
        hour=hh,
        minute=mm,
        second=0,
        microsecond=0
    )


    start = low_time - timedelta(
        hours=2
    )

    end = low_time + timedelta(
        hours=1
    )


    score = level(
        tide["height"]
    )



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


    event.add(
        "summary",
        f"🌊赶海 {score}"
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
{tide['time']}

潮高：
{tide['height']} cm

赶海指数：
{score}

建议：
低潮前2小时开始
"""
    )


    cal.add_component(
        event
    )


    with open(
        ICS_FILE,
        "wb"
    ) as f:

        f.write(
            cal.to_ical()
        )



if __name__=="__main__":

    create_calendar()

    print(
        "赶海日历生成完成"
    )
