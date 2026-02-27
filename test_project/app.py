
class Application:
    def __init__(self):
        self.running = False
    
    def run(self):
        self.running = True
        print("Running app")
    
    def stop(self):
        self.running = False
