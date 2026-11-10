import math
from multiprocessing import Pool, Process, Queue, Value, Lock
import hashlib

import requests

from saver import save_all


def process_post(post_data):
    body_length = len(post_data["body"])
    score = sum(math.sin(i) for i in range(1_000_000)) * body_length
    text_hash = hashlib.sha256(
        (post_data["title"] + post_data["body"]).encode("utf-8")
    ).hexdigest()
    post_data["complexity_score"] = score
    post_data["text_hash"] = text_hash
    return post_data


def fetch_post(post_id):
    try:
        response = requests.get(
            f'https://jsonplaceholder.typicode.com/posts/{post_id}'
        )
        response.raise_for_status()
        data = response.json()
        return process_post(data)
    except Exception as e:
        return {'error': str(e)}


def monitor(queue):
    while True:
        post_id = queue.get()
        if post_id is None:
            break
        print(f"[Monitor] Пост {post_id} обработан.")


_queue = None
_counter = None
_lock = None


def init_worker(queue, counter, lock):
    global _queue, _counter, _lock
    _queue = queue
    _counter = counter
    _lock = lock


def worker(post_id):
    result = fetch_post(post_id)
    _queue.put(post_id)
    if "error" not in result:
        with _lock:
            _counter.value += 1
    return result


if __name__ == '__main__':
    queue = Queue()
    counter = Value('i', 0)
    lock = Lock()

    monitor_process = Process(target=monitor, args=(queue,))
    monitor_process.start()

    with Pool(
        8,
        initializer=init_worker,
        initargs=(queue, counter, lock),
    ) as pool:
        results = pool.map(worker, range(1, 101))

    queue.put(None)
    monitor_process.join()

    print(results)
    print(f"Успешно обработано: {counter.value}")

    save_all(results)