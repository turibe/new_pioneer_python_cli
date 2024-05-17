from threading import Lock

print_lock = Lock()

def report(s):
    with print_lock:
        print(s)

DEBUG = False
