import concurrent.futures
import threading
import queue
import time
import random
import uuid

from gptwntranslator.helpers.design_patterns_helper import singleton


class APICallQueue:
    def __init__(self):
        self._initialize()
        self._id = None

    def _initialize(self):
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self._task_queue = queue.Queue()
        self._results = {}
        self._active_tasks = 0
        self._task_lock = threading.Lock()
        self._task_condition = threading.Condition(self._task_lock)

    def start(self):
        monitor = APICallQueueMonitor()
        self._id = monitor.add_queue(self)
        self._executor.submit(self._worker)

    def stop(self):
        self._task_queue.put((None, None, None, None))
        self._executor.shutdown(wait=True)
        monitor = APICallQueueMonitor()
        monitor.remove_queue(self._id)

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

@singleton
class APICallQueueSingleton(APICallQueue):
    pass

@singleton
class APICallQueueMonitor:
    def __init__(self):
        self._active_queues = dict()

    def add_queue(self, queue: APICallQueue) -> str:
        queue_id = uuid.uuid4()
        self._active_queues[queue_id] = queue
        return queue_id
    
    def remove_queue(self, queue_id: str):
        self._active_queues.pop(queue_id)

    def stop_all(self):
        for _, queue in self._active_queues.items():
            queue.stop()