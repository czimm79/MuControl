import XInput as xi
from time import sleep

connected = xi.get_connected()
events = xi.get_events()

state = xi.get_state(1)

loops = 0
while loops < 100000:
    loops += 1
    sleep(0.001)
    events = xi.get_events()
    for event in events:
        print(event)
