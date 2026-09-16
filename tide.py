from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import math


# ==========================
# 青岛北站白泥地赶海日历
# ==========================

tz = pytz.timezone("Asia/Shanghai")


cal = Calendar()

cal.add(
    "prodid",
    "-//Qingdao Bainidi Tide Calendar//CN"
)

cal.add(
    "version",
    "2.0"
)

cal.add(
    "X-WR-CALNAME",
    "🌊白泥地赶海"
)


# ==========================
# 模拟潮汐模型
# 后续可以替换真实API
# ==========================


def tide_height(day):
    """
    根据日期模拟潮汐大小
    以后接API只替换这里
    """

    # 月周期
    cycle = day % 15

    if cycle in [0,1,14]:
        return 0.7       # 大潮

    elif cycle in [2,3,12,13]:
        return 1.0

    else:
        return 1.5



def tide_level_text(h):

    if h <= 0.8:
        return "⭐⭐⭐⭐⭐"

    elif h <= 1.2:
        return "⭐⭐⭐⭐"

    elif h <= 1.8:
        return "⭐⭐⭐"

    else:
        return "⭐"



# ==========================
# 生成未来一年
# ==========================


start = datetime.now()


for i in range(365):

    day = start + timedelta(days=i)


    # 模拟低潮时间
    # 实际以后换API
    low_hour = 6 + (i % 6)


    low_time = day.replace(
        hour=low_hour,
        minute=20,
        second=0,
        microsecond=0
    )


    height = tide_height(i)


    score = tide_level_text(height)


    event = Event()


    event.add(
        "summary",
        f"🌊赶海 {score}"
    )


    event.add(
        "dtstart",
        tz.localize(
            low_time - timedelta(hours=2)
        )
    )


    event.add(
        "dtend",
        tz.localize(
            low_time + timedelta(hours=1)
        )
    )


    description = f"""
地点：
青岛北站白泥地

最低潮：
{low_time.strftime('%H:%M')}

潮高：
{height} 米

赶海指数：
{score}

建议：
低潮前2小时到低潮后1小时
"""


    event.add(
        "description",
        description
    )


    event.add(
        "location",
        "青岛北站白泥地公园"
    )


    cal.add_component(event)



# 输出文件

with open(
    "qingdao_bainidi.ics",
    "wb"
) as f:

    f.write(
        cal.to_ical()
    )


print(
    "生成完成 qingdao_bainidi.ics"
)
