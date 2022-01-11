from jinja2 import Environment, FileSystemLoader, select_autoescape
from json import load
import datetime

class web:
    def __init__(self):
        self.env = env = Environment(loader=FileSystemLoader("www"), autoescape=select_autoescape())
        self.template = env.get_template("index_template.html")

        self.make()
    
    def format_day(self, date):
        
        datetime_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        
        worded_day = datetime_date.strftime('%A')
        numbered_day = datetime_date.strftime('%Y-%m-%d')
        
        full_day = f'{worded_day} {numbered_day}'
        
        return full_day
    
    def make(self):
        
        bookings = [
                        load(open(f"dat/rooms_{i}.json"))['data'] for i in range(7) 
                    ]
        
        bookings.sort(key=lambda x: x[0]['session_start'])
        
        room_bookings = list()
        
        for i, day in enumerate(bookings):
            day_string = self.format_day(day[0]['session_start'])
            room_bookings.append([day_string])
            
            for j, booking in enumerate(day):
                room_bookings[i].append(booking['room_name'])
        
        print(room_bookings)
        
        with open("www/index.html", "w") as file:
            file.write(self.template.render(room_bookings=room_bookings))
            
web = web()