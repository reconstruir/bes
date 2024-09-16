#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import time
import pytz

from datetime import datetime
from datetime import timezone
from zoneinfo import ZoneInfo

class btimezone(object):
  'Stuff to help dealing with timezones'

  # Define a mapping of time zone offsets to full time zone names
  # Note: This mapping is simplified and does not cover all time zones.
  TIME_ZONE_MAPPING = {
    -12: 'Pacific/Kwajalein',
    -11: 'Pacific/Samoa',
    -10: 'Pacific/Honolulu',
    -9: 'America/Anchorage',
    -8: 'America/Los_Angeles',
    -7: 'America/Denver',
    -6: 'America/Chicago',
    -5: 'America/New_York',
    -4: 'America/Atlantic',
    -3: 'America/Argentina/Buenos_Aires',
    -2: 'Atlantic/Azores',
    -1: 'Atlantic/Cape_Verde',
    0: 'Europe/London',
    1: 'Europe/Paris',
    2: 'Europe/Bucharest',
    3: 'Europe/Moscow',
    4: 'Asia/Dubai',
    5: 'Asia/Karachi',
    6: 'Asia/Dhaka',
    7: 'Asia/Bangkok',
    8: 'Asia/Singapore',
    9: 'Asia/Tokyo',
    10: 'Australia/Sydney',
    11: 'Pacific/Efate',
    12: 'Pacific/Fiji'
  }
  
  @classmethod
  def local_timezone_name(clazz):
    'Return the name of the current local timezone.'

    'Return the name of the current local timezone.'
    now = datetime.now(timezone.utc)
    offset = now.utcoffset().total_seconds() / 3600
    offset = round(offset)
    return clazz.TIME_ZONE_MAPPING.get(offset, 'Unknown')    
#    is_dst = time.localtime().tm_isdst > 0
#    utc_offset_seconds = -time.altzone if is_dst else -time.timezone
#    utc_offset_hours = utc_offset_seconds / 3600
#    timezone_name = time.tzname[is_dst]
#    return timezone_name

  @classmethod
  def xlocal_timezone(clazz):
    'Return the ZoneInfo of the current local timezone.'

    name = clazz.local_timezone_name()
    tzinfo = ZoneInfo(name)
    return tzinfo

  @classmethod
  def local_timezone(clazz):
    return datetime.datetime.now().astimezone().tzinfo 
  
  def get_local_time_zone_name():
    now = datetime.datetime.now(datetime.timezone.utc)
    # Retrieve the offset in hours
    offset = now.utcoffset().total_seconds() / 3600
    # Find the closest matching time zone name
    # (This may need adjustment for daylight saving time)
    offset = round(offset)  # Round to the nearest hour
    return TIME_ZONE_MAPPING.get(offset, 'Unknown time zone')  
