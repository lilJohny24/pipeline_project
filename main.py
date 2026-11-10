import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

from anylazer import process_post
from fetcher import fetch_all_posts
from saver import save_all


def run_pipeline():
    start = time.perf_counter()

    # Часть 1: HTTP 
    fetched = asyncio.run(fetch_all_posts())
    total = len(fetched)
    # Фильтр: None и {'error': ...} (потому что fetcher возвращает dict при ошибке)
    loaded = [p for p in fetched if p is not None and "error" not in p]

    # Часть 2: CPU
    with ProcessPoolExecutor(max_workers=8) as pool:
        processed = list(pool.map(process_post, loaded))

    # Часть 3: I/O 
    saved = save_all(processed)

    elapsed = time.perf_counter() - start

    print("=== Отчёт о работе пайплайна ===")
    print(f"Запрошено постов: {total}")
    print(f"Успешно загружено: {len(loaded)}")
    print(f"Успешно обработано (CPU): {len(processed)}")
    print(f"Успешно сохранено (I/O): {saved}")
    print(f"Общее время: {elapsed:.2f} сек.")


if __name__ == "__main__":
    run_pipeline()