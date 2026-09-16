#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青岛北站白泥地赶海日历
自动获取未来30天潮汐，生成 tide.ics。
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from icalendar import Calendar, Event, Alarm

LATITUDE = 36.1698
LONGITUDE = 120.3820
DAYS = 30
TZ = timezone(timedelta(hours=8))
API = "https://api.openwaters.io/tides/extremes"

def parse_time(value):
    if value is None:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt.astimezone(TZ)
    except ValueError:
        return None

def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def get_tides():
    start = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=DAYS + 1)
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "units": "meters",
    }
    url = API + "?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "qingdao-bainidi-calendar/3.0"})
    with urlopen(req, timeout=30) as response:
        raw = response.read().decode("utf-8")
        if response.status != 200:
            raise RuntimeError(f"潮汐 API HTTP {response.status}: {raw[:500]}")
    data = json.loads(raw)

    # Open Waters 实际常见格式：
    # {"extremes":[{"time":"...","type":"HIGH/LOW","height":...}]}
    candidates = data.get("extremes", []) if isinstance(data, dict) else data
    result = []
    for item in candidates or []:
        if not isinstance(item, dict):
            continue
        dt = parse_time(item.get("time") or item.get("datetime"))
        kind = str(item.get("type") or item.get("event") or item.get("label") or "").upper()
        # Open Waters / Neaps 当前返回格式使用 low/high 布尔字段，水位字段叫 level
        is_low = (
            item.get("low") is True
            or kind in ("LOW", "LOWTIDE", "EBB")
            or kind.startswith("LOW")
        )
        height = number(item.get("height", item.get("level", item.get("waterLevel"))))
        if dt and is_low:
            if start <= dt < end:
                result.append((dt, height))
    return sorted(result, key=lambda x: x[0])

def main():
    now = datetime.now(TZ)
    lows = get_tides()
    if not lows:
        raise RuntimeError(
            "API 没有解析到低潮数据。请检查 Actions 中 API 原始返回；"
            "当前接口格式应使用 low=true、time、level 字段。"
        )

    cal = Calendar()
    cal.add("prodid", "-//Qingdao Bainidi Tide Calendar//CN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("X-WR-CALNAME", "青岛北站白泥地赶海")
    cal.add("X-WR-TIMEZONE", "Asia/Shanghai")

    for dt, height in lows:
        event = Event()
        event.add("uid", f"bainidi-low-{dt:%Y%m%d%H%M}@calendar.local")
        event.add("dtstamp", now)
        event.add("dtstart", dt - timedelta(hours=2))
        event.add("dtend", dt + timedelta(hours=1))
        event.add("summary", f"🌊赶海 {dt:%H:%M}")
        h = f"{height:.2f}m" if height is not None else "未知"
        event.add("description", f"地点：青岛北站白泥地\n低潮：{dt:%Y-%m-%d %H:%M}\n潮高：{h}\n建议时段：低潮前2小时至低潮后1小时")
        event.add("location", "青岛北站白泥地")
        event.add("transp", "OPAQUE")
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", "🌊赶海提醒")
        alarm.add("trigger", timedelta(hours=-3))
        event.add_component(alarm)
        cal.add_component(event)

    Path("tide.ics").write_bytes(cal.to_ical())
    print(f"成功生成 tide.ics，共 {len(lows)} 个低潮事件。")

if __name__ == "__main__":
    main()
