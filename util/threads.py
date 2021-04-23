import threading


def divide_in_chunks(alist: list, num: int):
    length = len(alist)
    chunk_size = (length // num)
    for i in range(0, length, chunk_size):
        yield alist[i: i+chunk_size]


def start_with_threads(task, data: list):
    num_threads = 20
    data_chunks = list(divide_in_chunks(data, num_threads))

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=task,
                                  args=(data_chunks[i],))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
