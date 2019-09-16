import XInput as xi
from time import sleep


def filter_events(event):
    if event.type == 4:
        print(event.button)

loops = 0
while loops < 100000:
    loops += 1
    sleep(0.0001)
    events = xi.get_events()
    for event in events:
        filter_events(event)




# connected = xi.get_connected()
# print(connected)
#
# if any(controller is True for controller in connected):
#     print("A controller is connected!")
# else:
#     print("No controller connected.")

