from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

TZ = pytz.timezone("Asia/Shanghai")

def get_tide():
    now = datetime.now(TZ)
    return [{"time": now.replace(hour=12, minute=0, second=0, microsecond=0),
             "height": 0.8}]

def make_calendar(data):
    cal = Calendar()
    cal.add("prodid", "-//Qingdao Bainidi Tide//CN")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", "🌊白泥地公园赶海")

    for item in data:
        event = Event()
        low = item["time"]
        event.add("summary", f"🌊白泥地赶海 潮高{item['height']}米")
        event.add("dtstart", low - timedelta(hours=2))
        event.add("dtend", low + timedelta(hours=1))
        event.add("description", "地点：青岛北站白泥地公园")
        cal.add_component(event)

    return cal

if __name__ == "__main__":
    with open("qingdao_bainidi.ics", "wb") as f:
        f.write(make_calendar(get_tide()).to_ical())
