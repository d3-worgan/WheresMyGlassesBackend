import multiprocessing
import time

def process_request():
    for _ in range(10):
        print("Requests")
        time.sleep(1)


def run_in_background():
    for _ in range(10):
        print("Background")
        time.sleep(1)


if __name__ == '__main__':

    print("Multithreading...")
    #ol = ObjectLocator(100)

    print("Creating processes")
    pBackground = multiprocessing.Process(target=run_in_background)
    pRequests = multiprocessing.Process(target=process_request)

    print("Starting processes...")
    pBackground.start()
    pRequests().start()
