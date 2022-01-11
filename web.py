from jinja2 import Environment, FileSystemLoader, select_autoescape
from json import load
import datetime

class web:
    def __init__(self):
        self.env = env = Environment(loader=FileSystemLoader("www"), autoescape=select_autoescape())
        self.template = env.get_template("index_template.html")

        self.make()
    
    def make(self):
        
        bookings = [
            load(open(f"dat/rooms_{i}.json"))['data'] for i in range(7)
        ]
        bookings.sort(key=lambda x: x[0]['session_start'])
        
        room_bookings = dict()
        
        for day in bookings:
            
            for booking in day:
                
                print(booking)
        
        # with open("www/index.html", "w") as file:

        #     file.write(self.template.render(test="testing", onetwothree="123"))
            
web = web()