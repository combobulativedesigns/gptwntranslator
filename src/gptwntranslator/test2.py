import concurrent.futures
import threading
import queue
import time
import random

class CallQueue:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self._task_queue = queue.Queue()
        self._results = {}
        self._active_tasks = 0
        self._task_lock = threading.Lock()

    def _exponential_backoff(self, retries, base_delay=0.5, max_delay=60.0, jitter=True):
        delay = min(max_delay, base_delay * (2 ** retries))
        if jitter:
            delay = random.uniform(base_delay, delay)
        return delay

    def _worker(self):
        while True:
            task_id, func, params, retries = self._task_queue.get()
            if task_id is None:
                break
            try:
                result = func(**params)
            except Exception as e:
                if retries > 0:
                    backoff_time = self._exponential_backoff(retries)
                    time.sleep(backoff_time)
                    self._task_queue.put((task_id, func, params, retries - 1))
                else:
                    result = e
            else:
                self._results[task_id] = result
            finally:
                with self._task_lock:
                    self._active_tasks -= 1

    def start(self, num_workers=4):
        self._workers = [threading.Thread(target=self._worker) for _ in range(num_workers)]
        for worker in self._workers:
            worker.start()

    def stop(self):
        for _ in self._workers:
            self._task_queue.put((None, None, None, None))
        for worker in self._workers:
            worker.join()

    def add_call(self, func, retries=3, **params):
        task_id = id(params)
        with self._task_lock:
            self._active_tasks += 1
        self._task_queue.put((task_id, func, params, retries))
        return task_id

    def get_result(self, task_id):
        return self._results.pop(task_id, None)

    def wait(self):
        while True:
            with self._task_lock:
                if self._active_tasks == 0:
                    break
            time.sleep(0.1)

# Usage example:


def api_function(param1, param2):
    sleep_time = random.randint(5, 10)
    time.sleep(sleep_time)
    result = f"param1={param1}, param2={param2}, sleep_time={sleep_time}"
    return result

def main():
    call_queue = CallQueue()
    call_queue.start()

    task_ids = [
        call_queue.add_call(api_function, param1='value1', param2='value2'),
        call_queue.add_call(api_function, param1='value3', param2='value4'),
        # Add more calls as needed
    ]

    # Wait for all tasks to complete
    call_queue.wait()

    # Get results
    for task_id in task_ids:
        result = call_queue.get_result(task_id)
        print(f"Result: {result}")

    call_queue.stop()

if __name__ == '__main__':
    main()
