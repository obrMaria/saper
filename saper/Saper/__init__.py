# __init__.py
from Saper.saper import Saper
from Saper.db import initialize_db

def show():
    initialize_db()
    Saper().show()