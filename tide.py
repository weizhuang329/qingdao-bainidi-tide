#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青岛北站白泥地公园潮汐日历
每天运行一次，生成未来约16天的潮汐日历 tide.ics。
说明：Open-Meteo Marine 的海平面网格数据在近岸属于估算值，
请把它作为赶海时间参考，不替代当地官方潮汐预报。
"""

from datetime import datetime, timedelta
from pathlib import Path
import json
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event, Alarm

LATITUDE = 36.18
LONGITUDE = 120.35
TIMEZONE = "Asia/Shanghai"
OUTPUT = Path("tide.ics")
DAYS = 16

def fetch_hourly():
    params = urllib.parse.urlencode({
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "sea_level_height_msl",
        "forecast_days": DAYS,
        "timezone": TIMEZONE,
    })
    url = "https://marine-api.open-meteo.com/v1/marine?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "qingdao-bainidi-tide/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)

    times = data.get("hourly", {}).get("time", [])
    levels = data.get("hourly", {}).get("sea_level_height_msl", [])
    if not times or not levels or len(times) != len(levels):
        raise RuntimeError("潮汐接口没有返回有效的小时海平面数据。")
    return times, levels

def find_low_tides(times, levels):
    lows = []
    for i in range(1, len(levels) - 1):
        a, b, c = levels[i-1], levels[i], levels[i+1]
        if None in (a, b, c):
            continue
        if b <= a and b <= c and (b < a or b < c):
            dt = datetime.fromisoformat(times[i]).replace(tzinfo=ZoneInfo(TIMEZONE))
            lows.append((dt, float(b)))
    # 同一天如果有多个低潮全部保留；去掉过近的重复极值
    result = []
    for item in lows:
        if not result or item[0] - result[-1][0] >= timedelta(hours=3):
            result.append(item)
    return result

def make_event(dt, height):
    cal_event = Event()
    uid = f"qingdao-bainidi-{dt.strftime('%Y%m%d%H%M')}-{int(round(height*100))}@calendar.local"
    cal_event.add("uid", uid)
    cal_event.add("dtstamp", datetime.now(ZoneInfo("UTC")))
    cal_event.add("summary", f"赶海 {dt:%H:%M}")
    cal_event.add("dtstart", dt - timedelta(hours=2))
    cal_event.add("dtend", dt + timedelta(hours=1))
    cal_event.add("description",
                   f"地点：青岛北站白泥地公园\\n"
                   f"最低潮：{dt:%Y-%m-%d %H:%M}\\n"
                   f"潮高估算：{height:.2f} 米\\n"
                   "建议：低潮前约2小时到低潮后约1小时；请注意泥滩湿滑和现场安全。")
    cal_event.add("location", "青岛北站白泥地公园")
    alarm = Alarm()
    alarm.add("action", "DISPLAY")
    alarm.add("description", "赶海提醒")
    alarm.add("trigger", timedelta(hours=-3))
    cal_event.add_component(alarm)
    return cal_event

def main():
    times, levels = fetch_hourly()
    lows = find_low_tides(times, levels)
    if len(lows) < 5:
        raise RuntimeError(f"只解析到 {len(lows)} 个低潮点，数据可能异常，请检查 API 返回。")

    cal = Calendar()
    cal.add("prodid", "-//Qingdao Bainidi Tide Calendar//CN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", "青岛赶海潮汐")
    cal.add("x-wr-timezone", TIMEZONE)
    for dt, height in lows:
        cal.add_component(make_event(dt, height))

    OUTPUT.write_bytes(cal.to_ical())
    print(f"成功生成 {OUTPUT}，共 {len(lows)} 个低潮事件。")
    print("覆盖时间：", times[0], "至", times[-1])

if __name__ == "__main__":
    main()
