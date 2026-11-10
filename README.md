# Pipeline Project          


### ПЕРЕД ЗАПУСКОМ УСТАНОВИТЕ БИБЛИОТЕКИ ЧЕРЕЗ КОМАНДУ: "pip install -r requirements.txt"

### ДЛЯ СТАРТА ПРОГРАММЫ ВВЕДИТЕ КОМАНДУ: "python main.py"



## Architecture Choices

## Часть 1 — `asyncio` + `aiohttp`
HTTP — I/O-bound: поток ждёт сеть. 100 корутин в одном потоке дешевле 100 потоков/процессов. `Semaphore(5)` — лимит одновременных запросов, `return None` при ошибке — фильтр в `main.py`.

## Часть 2 — `multiprocessing`
CPU-bound (`sum(sin)` + SHA-256): GIL не даёт потокам параллелизма, нужны процессы. 8 воркеров = 8 ядер. `process_post` вынесен в `anylazer.py` и импортируется в `main.py`.

## Часть 3 — `threading`
I/O-bound. Потоки проще `asyncio`, `queue.Queue` — потокобезопасная труба, `threading.Event` — сигнал завершения и прерываемый sleep, `threading.Lock` — атомарный `saved_count`.

## Часть 4 — `main.py`
Части зависимы — конвейер, параллелить нечего. `ProcessPoolExecutor` в `with` даёт `shutdown(wait=True)` автоматически. `perf_counter` — монотонные часы для точного замера.




### Под конец возникли трудности со сборкой пайплайна: части 2 и 3 были смешаны, `save_all` возвращал `0` из-за локальной `saved_count`, `fetcher.fetch_all_posts` требовал аргумент и ### еще некоторые моменты. С этой проблемой помогла сильно нейронка. 

### Еще я узнал о большем функционале некоторых методов, например методы из библиотеки math и hashlib. Освоил параметры которые может принимать with Pool, ThreadPoolExecutor.

