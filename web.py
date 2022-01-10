from jinja2 import Environment, FileSystemLoader, select_autoescape
from os import path 

env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())

template = env.get_template("index_template.html")

with open("index.html", "w") as file:

    file.write(template.render(test="testing", onetwothree="123"))