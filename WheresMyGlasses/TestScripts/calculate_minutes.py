from datetime import datetime
import time



def minutes_passed(snaptime):
    current_time = datetime.now()
    passed = current_time - snaptime
    minutes_passed = passed.seconds / 60
    return round(minutes_passed, 2)


snapshot_time = datetime.now()

time.sleep(2)

minutes_passed = minutes_passed(snapshot_time)

print(minutes_passed)



# start = datetime.now()
#
# start_time = start.strftime("%H:%M:%S")
#
# time.sleep(2)
#
# end = datetime.now()
#
# end_time = end.strftime("%H:%M:%S")
#
#
#
# print(start_time)
# print(end_time)
#
# passed = end - start
#
# seconds = passed.seconds
# print(passed)
# print(seconds)
#
# minutes = seconds / 60
#
# print(round(minutes, 2))