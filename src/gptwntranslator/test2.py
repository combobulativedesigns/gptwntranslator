import concurrent.futures
import threading
import queue
import time
import random
import uuid

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
        self._task_condition = threading.Condition(self._task_lock)

    def start(self):
        self._executor.submit(self._worker)

    def stop(self):
        self._task_queue.put((None, None, None, None))
        self._executor.shutdown(wait=True)

    def add_call(self, func, retries=3, **params):
        task_id = uuid.uuid4()
        with self._task_lock:
            self._active_tasks += 1
        self._task_queue.put((task_id, func, params, retries, self._handle_result))
        return task_id
    
    def get_result(self, task_id):
        return self._results.pop(task_id, None)

    def _worker(self):
        while True:
            task_id, func, params, retries, callback = self._task_queue.get()
            if task_id is None:
                break
            try:
                result = func(**params)
            except Exception as e:
                if retries > 0:
                    backoff_time = self._exponential_backoff(retries)
                    time.sleep(backoff_time)
                    self._task_queue.put((task_id, func, params, retries - 1, callback))
                else:
                    callback(task_id, e)
            else:
                callback(task_id, result)

    def _handle_result(self, task_id, result):
        with self._task_lock:
            self._results[task_id] = result
            self._active_tasks -= 1
            self._task_condition.notify_all()

    def _exponential_backoff(self, retries_left):
        max_retries = 3
        exp_base = 2
        sleep_time = exp_base ** (max_retries - retries_left) + random.uniform(0, 0.1)
        return sleep_time

    def wait(self):
        with self._task_condition:
            while self._active_tasks > 0:  # Wait while there are active tasks
                self._task_condition.wait()  # Wait for a notification

def api_function(param1, param2):
    time.sleep(5)

    if param1 == 'value1' and param2 == 'value2':
        raise ValueError("Simulated exception for value1 and value2")

    return f"Result for {param1}, {param2}"

def main():
    call_queue = CallQueue()
    call_queue.start()

    task_ids = [
        call_queue.add_call(api_function, param1='value1', param2='value2'),
        call_queue.add_call(api_function, param1='value3', param2='value4')
    ]

    call_queue.wait()

    for task_id in task_ids:
        result = call_queue.get_result(task_id)
        if isinstance(result, ValueError):
            print(f"Error: {result}")
        else:
            print(f"Result: {result}")

    call_queue.stop()

if __name__ == '__main__':
    main()
