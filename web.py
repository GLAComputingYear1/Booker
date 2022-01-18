from jinja2 import Environment, FileSystemLoader, select_autoescape
from json import load
import datetime

class web:
    def __init__(self):
        self.env = env = Environment(loader=FileSystemLoader("old/www"), autoescape=select_autoescape())
        self.template = env.get_template("index_template.html")
        self.make()
    
    def format_day(self, date):
        
        datetime_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        worded_day = datetime_date.strftime('%A')
        numbered_day = datetime_date.strftime('%Y-%m-%d')
                
        return f'{worded_day} {numbered_day}'
    
    def make(self):
        
        bookings = [
                        load(open(f"old/dat/rooms_{i}.json"))['data'] for i in range(7)
                    ]
        
        bookings.sort(key=lambda x: x[0]['session_start'])
        
        room_bookings = list()
        
        for i, day in enumerate(bookings):
            day_string = self.format_day(day[0]['session_start'])
            room_bookings.append([day_string])
            
            for booking in day:
                room_bookings[i].append(booking['room_name'])
        
        with open("www/index.html", "w") as file:
            file.write(self.template.render(room_bookings=room_bookings))

web = web()