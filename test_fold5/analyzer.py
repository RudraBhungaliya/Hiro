from utils import compute_average

def analyze(data):
    if not data:
        return "No data above threshold."
    avg = compute_average(data)
    return f"Average of filtered data: {avg}"
