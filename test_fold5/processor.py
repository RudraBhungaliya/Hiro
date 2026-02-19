from analyzer import analyze
from config import THRESHOLD

def process_data(data):
    filtered = [x for x in data if x > THRESHOLD]
    return analyze(filtered)
