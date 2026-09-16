#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

def fetch():
    start = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=DAYS + 1)
    url = API + "?" + urlencode({
        "latitude": LATITUDE, "longitude": LONGITUDE,
        "start": start.isoformat(), "end": end.isoformat(), "units": "meters"
    })
    req = Request(url, headers={"User-Agent": "qingdao-bainidi-calendar/2.0"})
    with urlopen(req, timeout=30) as r:
        if r.status != 200:
            raise RuntimeError(f"API HTTP {r.status}")
        return json.loads(r.read().decode("utf-8"))

def dt_parse(v):
    if not v: return None
    s = str(v).replace("Z", "+00:00")
    try: d = datetime.fromisoformat(s)
    except ValueError: return None
    return d.replace(tzinfo=TZ) if d.tzinfo is None else d.astimezone(TZ)

def scan(x):
    out = []
    if isinstance(x, list):
        for y in x: out += scan(y)
    elif isinstance(x, dict):
        tv = next((x[k] for k in ("time","timestamp","datetime","dateTime","date") if k in x), None)
        kind = next((str(x[k]).lower() for k in ("type","event","tideType","kind","name") if k in x), "")
        height = None
        for k in ("height","level","waterLevel","value"):
            if k in x:
                try: height = float(x[k])
                except (TypeError, ValueError): pass
                break
        d = dt_parse(tv)
        if d and kind: out.append((d, kind, height))
        else:
            for v in x.values():
                if isinstance(v, (dict,list)): out += scan(v)
    return out

def main():
    now = datetime.now(TZ)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    data = fetch()
    tides = sorted(scan(data), key=lambda z: z[0])
    cal = Calendar()
    cal.add("prodid", "-//Qingdao Bainidi Tide Calendar//CN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("X-WR-CALNAME", "青岛北站白泥地赶海")
    cal.add("X-WR-TIMEZONE", "Asia/Shanghai")
    count = 0
    for d, kind, height in tides:
        if not any(w in kind for w in ("low","ebb","低","低潮")): continue
        if not (start <= d < start + timedelta(days=DAYS + 1)): continue
        e = Event()
        e.add("uid", f"bainidi-{d:%Y%m%d%H%M}@calendar.local")
        e.add("dtstamp", now)
        e.add("dtstart", d - timedelta(hours=2))
        e.add("dtend", d + timedelta(hours=1))
        e.add("summary", f"🌊赶海 {d:%H:%M}")
        e.add("description", f"地点：青岛北站白泥地\n低潮：{d:%Y-%m-%d %H:%M}\n潮高：{height if height is not None else '未知'}m\n建议时段：低潮前2小时至低潮后1小时")
        e.add("location", "青岛北站白泥地")
        e.add("transp", "OPAQUE")
        a = Alarm()
        a.add("action","DISPLAY"); a.add("description", "🌊赶海提醒"); a.add("trigger", timedelta(hours=-3))
        e.add_component(a)
        cal.add_component(e); count += 1
    if count == 0: raise RuntimeError("没有解析到低潮数据，请查看 Actions 日志。")
    Path("tide.ics").write_bytes(cal.to_ical())
    print(f"生成 tide.ics：{count} 个事件")

if __name__ == "__main__": main()
