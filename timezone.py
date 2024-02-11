from datetime import datetime, timezone, timedelta

import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


def calculateTimestamp(date_str):
    try:
        # Parse the input date string
        date_object = datetime.strptime(date_str, '%m/%d/%Y')

        # Calculate the timestamp
        timestamp = date_object.timestamp()

        return timestamp
    except ValueError:
        return None  # Return None if the input date format is incorrect
    
def calculateSeconds(time_str):
    try:
        # Parse the input time string
        time_object = datetime.strptime(time_str, '%H:%M')

        # Calculate the total number of seconds
        total_seconds = time_object.hour * 3600 + time_object.minute * 60

        return total_seconds
    except ValueError:
        return None  # Return None if the input time format is incorrect
    
def breakdown_timestamp(timestamp):
    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp)

    # Extract individual components
    year = dt_object.year
    month = dt_object.month
    day = dt_object.day
    hour = dt_object.hour
    minute = dt_object.minute

    return year, month, day, hour, minute

def get_utc_offset(zone):
    place_timezone = pytz.timezone(zone)
    utc_offset = place_timezone.utcoffset(datetime.now())
    utc_offset = utc_offset.total_seconds() / 3600
    # print(utc_offset)
    return utc_offset

def get_timezone(city, state, zip_code, country):
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="timezoneFinder")
    location = geolocator.geocode(f'{state}')
    # print((location.latitude, location.longitude))
    timezoneFinder = TimezoneFinder()
    result = timezoneFinder.timezone_at(lng=location.longitude, lat=location.latitude)
    print("Time Zone : ", result)
    return result

def get_rfc2822_time(year, month, day, hour_24, minutes, time_zone):
    UTC_offset = get_utc_offset(time_zone)
    custom_timezone = timezone(timedelta(hours=UTC_offset))
    local_target_datetime = datetime(year, month, day, hour_24, minutes, tzinfo=custom_timezone)
    #print(local_target_datetime)
    rfc2822_time = local_target_datetime.strftime('%a, %d %b %Y %H:%M:%S %z')
    print("Converted Time in RFC2822 Format:", rfc2822_time)
    return rfc2822_time