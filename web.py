from jinja2 import Environment, FileSystemLoader, select_autoescape
from json import load
from collections import deque
import datetime

class web:
    def __init__(self):
        self.env = env = Environment(loader=FileSystemLoader("old/www"), autoescape=select_autoescape())
        self.template = env.get_template("index_template.html")
        self.make()
    
    def format_day(self, date, datetime_obj=None):
        datetime_date = datetime_obj
        if datetime_obj == None:
            datetime_date = datetime.datetime.strptime(date, '%H:%M')
        
        worded_day = datetime_date.strftime('%A')
        numbered_day = datetime_date.strftime('%Y-%m-%d')
                
        return f'{worded_day} {numbered_day}'
    
    def make(self):

        bookings = list()

        for i in range(7):
            try:
                file = open(f"old/dat/rooms_{i}.json")
                booking_data = load(file).get("data")
                file.close()
            except:
                booking_data = None

            bookings.append(booking_data)

        bookings = deque(bookings)
        bookings.rotate((datetime.datetime.today().weekday()+1))
        bookings = list(bookings)

        room_bookings = list()
        
        for i, day in enumerate(bookings):
            if day is not None:
                #datetime of booking = current date          - number of today's day in the week                       + number of booking's day in the week
                day_datetime_obj = datetime.datetime.today() - datetime.timedelta(datetime.datetime.today().weekday()) + (datetime.timedelta(i))
                # if booking is for next week, add 7 days
                day_datetime_obj += datetime.timedelta(7 if day_datetime_obj.day < datetime.datetime.today().day else 0)
                #format it
                day_string = self.format_day(None, day_datetime_obj)
                room_bookings.append([day_string])

                for booking in day:
                    room_bookings[i].append(booking['room_name'])
            else:
                day_string = "Null"
                room_bookings.append([day_string])
                room_bookings[i] += ["Null", "Null", "Null"]
        
        with open("www/index.html", "w") as file:
            file.write(self.template.render(room_bookings=room_bookings))

web = web()
