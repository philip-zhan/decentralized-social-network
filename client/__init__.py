from flask import Flask


app = Flask(__name__)
from client import views
