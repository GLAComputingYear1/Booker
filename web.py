from jinja2 import Environment, FileSystemLoader, select_autoescape
from os import path 

class web:
    def __init__(self):
        self.env = env = Environment(loader=FileSystemLoader("www"), autoescape=select_autoescape())
        self.template = env.get_template("index_template.html")

        self.make()
    
    def make(self):
        with open("www/index.html", "w") as file:

            file.write(self.template.render(test="testing", onetwothree="123"))