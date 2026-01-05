import time
from concurrent.futures import ThreadPoolExecutor


def task(n):
    time.sleep(0.1)
    return n * n


def single_thread():
    start = time.perf_counter()
    for i in range(8):
        task(i)
    end = time.perf_counter()
    print(f"Single-thread time: {end - start:.2f}s")


def multi_thread():
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=16) as executor:
        list(executor.map(task, range(8)))
    end = time.perf_counter()
    print(f"Multi-thread time: {end - start:.2f}s")


if __name__ == "__main__":
    single_thread()
    multi_thread()
