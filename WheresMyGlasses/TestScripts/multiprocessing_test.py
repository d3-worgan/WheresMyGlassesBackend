import time
import threading as th

keep_going = True
print("Start")

def key_capture_thread():
    """
    This function will run in a separate thread, to capture keyboard inputs used to terminate the program.
    This seems necessary because a lot of the runtime is spent in other threads handling acquisition, so ctrl+c
    doesn't work as nicely as it does in simpler programs.
    :return:
    """
    while True:
        time.sleep(2)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()


while keep_going:
    print("Running")
    time.sleep(1)
























# def do_something():
#     print('Sleeping 1 second')
#     time.sleep(1)
#     print('Done sleeping')
#
# def do_something2():
#     print('Sleeping 2 seconds')
#     time.sleep(2)
#     print('Done sleeping')
#
# def do_something3():
#     for _ in range(10):
#         print("do summin 3")
#
# def do_something4():
#     for _ in range(10):
#         print("do summin 4")
#
#
#
#
# if __name__ == "__main__":
#
#     start = time.perf_counter()
#
#     p1 = multiprocessing.Process(target=do_something3)
#     p2 = multiprocessing.Process(target=do_something4)
#
#     p1.start()
#     p2.start()
#
#  #   p1.join()
# #    p2.join()
#
#     finish = time.perf_counter()
#
#     print(f'Finished in {round(finish-start, 2)} second(s)')
