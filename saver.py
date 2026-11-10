from concurrent.futures import ThreadPoolExecutor
import queue
import threading
import time


lock = threading.Lock()
stop_event = threading.Event()


saved_count = 0
total_count = 0


def save_post(post_data):
    global saved_count
    time.sleep(0.05)
    title = post_data["title"][:40]
    line = (
        f"id={post_data['id']} | "
        f"title={title!r} | "
        f"score={post_data['complexity_score']:.2f} | "
        f"hash={post_data['text_hash'][:12]}...\n"
    )
    with lock:
        with open("results.log", "a", encoding="utf-8") as f:
            f.write(line)
        saved_count += 1


def worker(task_queue):
    while not stop_event.is_set():
        try:
            post_data = task_queue.get(timeout=0.1)
        except queue.Empty:
            continue
        try:
            save_post(post_data)
        finally:
            task_queue.task_done()


def progress_reporter():
    while not stop_event.is_set():
        with lock:
            current = saved_count
        print(f">>> Прогресс сохранения: {current} / {total_count}")
        stop_event.wait(timeout=0.5)


def save_all(results):
    global total_count, saved_count      # ← saved_count добавлен
    total_count = len(results)
    saved_count = 0                      # ← теперь это глобальная
    stop_event.clear()                   # ← сброс флага

    task_queue = queue.Queue()

    progress_thread = threading.Thread(target=progress_reporter, daemon=True)
    progress_thread.start()

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(worker, task_queue) for _ in range(3)]

        for post_data in results:
            task_queue.put(post_data)

        task_queue.join()

        stop_event.set()

        for f in futures:
            f.result()

    progress_thread.join()

    print(f">>> Прогресс сохранения: {saved_count} / {total_count}")
    return saved_count