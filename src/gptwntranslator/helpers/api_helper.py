# # import concurrent.futures
# # import threading
# # import queue
# # import time
# # import random
# # import uuid

# # from gptwntranslator.helpers.design_patterns_helper import singleton
# # from gptwntranslator.helpers.logger_helper import CustomLogger


# # logger = CustomLogger(__name__)

# # class APICallQueue:
# #     def __init__(self):
# #         self._initialize()
# #         self._id = None
# #         self._monitor = APICallQueueMonitor()

# #     def _initialize(self):
# #         self._executor = concurrent.futures.ThreadPoolExecutor()
# #         self._task_queue = queue.Queue()
# #         self._results = {}
# #         self._active_tasks = 0
# #         self._task_lock = threading.Lock()
# #         self._task_condition = threading.Condition(self._task_lock)

# #     def start(self):
# #         self._id = self._monitor.add_queue(self)
# #         logger.debug(f"Starting API call queue with id: {self._id}")
# #         self._executor.submit(self._worker)

# #     def stop(self):
# #         logger.debug(f"Stopping API call queue with id: {self._id}")
# #         self._task_queue.put((None, None, None, None))
# #         self._executor.shutdown(wait=True)
# #         self._monitor.remove_queue(self._id)

# #     def add_call(self, func, retries=3, **params):
# #         logger.debug(f"Adding API call to queue with id: {self._id}, func: {func.__name__}")
# #         task_id = uuid.uuid4()
# #         with self._task_lock:
# #             self._active_tasks += 1
# #         self._task_queue.put((task_id, func, params, retries, self._handle_result))
# #         return task_id
    
# #     def get_result(self, task_id):
# #         return self._results.pop(task_id, None)

# #     def _worker(self):
# #         while True:
# #             task_id, func, params, retries, callback = self._task_queue.get()
# #             if task_id is None:
# #                 break
# #             try:
# #                 logger.info(f"Executing API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__}")
# #                 result = func(**params)
# #             except Exception as e:
# #                 if retries > 0:
# #                     backoff_time = self._exponential_backoff(retries)
# #                     logger.debug(f"API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__} failed, retrying in {backoff_time} seconds")
# #                     time.sleep(backoff_time)
# #                     self._task_queue.put((task_id, func, params, retries - 1, callback))
# #                 else:
# #                     logger.error(f"API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__} failed")
# #                     callback(task_id, e)
# #             else:
# #                 logger.debug(f"API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__} succeeded")
# #                 callback(task_id, result)

# #     def _handle_result(self, task_id, result):
# #         with self._task_lock:
# #             self._results[task_id] = result
# #             self._active_tasks -= 1
# #             self._task_condition.notify_all()

# #     def _exponential_backoff(self, retries_left):
# #         max_retries = 3
# #         exp_base = 2
# #         sleep_time = exp_base ** (max_retries - retries_left) + random.uniform(0, 0.1)
# #         return sleep_time

# #     def wait(self):
# #         with self._task_condition:
# #             while self._active_tasks > 0:  # Wait while there are active tasks
# #                 self._task_condition.wait()  # Wait for a notification

# # @singleton
# # class APICallQueueSingleton(APICallQueue):
# #     pass

# # @singleton
# # class APICallQueueMonitor:
# #     def __init__(self):
# #         self._active_queues = dict()
# #         self._lock = threading.Lock()

# #     def add_queue(self, queue: APICallQueue) -> str:
# #         with self._lock:
# #             queue_id = uuid.uuid4()
# #             self._active_queues[queue_id] = queue
# #         return queue_id

# #     def remove_queue(self, queue_id: str):
# #         with self._lock:
# #             self._active_queues.pop(queue_id)

# #     def stop_all(self):
# #         with self._lock:
# #             for _, queue in self._active_queues.items():
# #                 queue.stop()

# import asyncio
# from functools import partial
# import random
# import uuid
# import threading

# from gptwntranslator.helpers.design_patterns_helper import singleton
# from gptwntranslator.helpers.logger_helper import CustomLogger

# logger = CustomLogger(__name__)

# # class APICallQueue:
# #     def __init__(self):
# #         self._initialize()
# #         self._id = None
# #         self._monitor = APICallQueueMonitor()

# #     def _initialize(self):
# #         self._task_queue = asyncio.Queue()
# #         self._results = {}
# #         self._active_tasks = 0
# #         self._task_lock = asyncio.Lock()
# #         self._task_condition = asyncio.Condition(self._task_lock)

# #     async def start(self):
# #         self._id = self._monitor.add_queue(self)
# #         logger.debug(f"Starting API call queue with id: {self._id}")
# #         self._worker_task = asyncio.create_task(self._worker())

# #     async def stop(self):
# #         logger.debug(f"Stopping API call queue with id: {self._id}")
# #         await self._task_queue.put((None, None, None, None))
# #         await self._worker_task
# #         self._monitor.remove_queue(self._id)

# #     async def add_call(self, func, retries=3, **params):
# #         logger.debug(f"Adding API call to queue with id: {self._id}, func: {func.__name__}")
# #         task_id = uuid.uuid4()
# #         async with self._task_lock:
# #             self._active_tasks += 1
# #         await self._task_queue.put((task_id, func, params, retries, self._handle_result))
# #         return task_id
    
# #     def get_result(self, task_id):
# #         return self._results.pop(task_id, None)

# #     async def _worker(self):
# #         while True:
# #             task_id, func, params, retries, callback = await self._task_queue.get()
# #             if task_id is None:
# #                 break
# #             try:
# #                 logger.info(f"Executing API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__}")
# #                 result = await func(**params)
# #             except Exception as e:
# #                 if retries > 0:
# #                     backoff_time = self._exponential_backoff(retries)
# #                     logger.debug(f"API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__} failed, retrying in {backoff_time} seconds")
# #                     await asyncio.sleep(backoff_time)
# #                     await self._task_queue.put((task_id, func, params, retries - 1, callback))
# #                 else:
# #                     logger.error(f"API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__} failed")
# #                     callback(task_id, e)
# #             else:
# #                 logger.debug(f"API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__} succeeded")
# #                 callback(task_id, result)

# #     async def _handle_result(self, task_id, result):
# #         async with self._task_lock:
# #             self._results[task_id] = result
# #             self._active_tasks -= 1
# #             self._task_condition.notify_all()

# #     def _exponential_backoff(self, retries_left):
# #         max_retries = 3
# #         exp_base = 2
# #         sleep_time = exp_base ** (max_retries - retries_left) + random.uniform(0, 0.1)
# #         return sleep_time

# #     async def wait(self):
# #         async with self._task_condition:
# #             while self._active_tasks > 0:  # Wait while there are active tasks
# #                 await self._task_condition.wait()
# #         await self._worker_task

# # class APICallQueue:
# #     def __init__(self):
# #         self._initialize()
# #         self._id = None
# #         self._monitor = APICallQueueMonitor()

# #     def _initialize(self):
# #         self._tasks = []
# #         self._results = {}
# #         self._task_lock = asyncio.Lock()

# #     def start(self):
# #         self._id = self._monitor.add_queue(self)
# #         logger.debug(f"Starting API call queue with id: {self._id}")
# #         self._loop = asyncio.new_event_loop()
# #         self._thread = threading.Thread(target=self._loop.run_forever)
# #         self._thread.start()

# #     def stop(self):
# #         logger.debug(f"Stopping API call queue with id: {self._id}")
# #         for task in self._tasks:
# #             task.cancel()
# #         self._loop.call_soon_threadsafe(self._loop.stop)
# #         self._thread.join()
# #         self._monitor.remove_queue(self._id)

# #     def add_call(self, func, retries=3, **params):
# #         logger.debug(f"Adding API call to queue with id: {self._id}, func: {func.__name__}")
# #         task_id = uuid.uuid4()
# #         task = asyncio.ensure_future(self._execute_call(task_id, func, params, retries), loop=self._loop)
# #         self._tasks.append(task)
# #         return task_id

# #     async def _execute_call(self, task_id, func, params, retries):
# #         try:
# #             logger.info(f"Executing API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__}")
# #             callback = partial(self._handle_result, task_id)
# #             await self._loop.run_in_executor(None, func, **params, callback=callback)
# #         except Exception as e:
# #             if retries > 0:
# #                 backoff_time = self._exponential_backoff(retries)
# #                 logger.debug(f"API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__} failed, retrying in {backoff_time} seconds")
# #                 await asyncio.sleep(backoff_time)
# #                 await self._execute_call(task_id, func, params, retries - 1)
# #             else:
# #                 logger.error(f"API call in queue with id: {self._id}, task: {task_id}, func: {func.__name__} failed")
# #                 await self._handle_result(task_id, e)

# #     async def _handle_result(self, task_id, result):
# #         async with self._task_lock:
# #             self._results[task_id] = result

# #     def _exponential_backoff(self, retries_left):
# #         max_retries = 3
# #         exp_base = 2
# #         sleep_time = exp_base ** (max_retries - retries_left) + random.uniform(0, 0.1)
# #         return sleep_time

# #     async def wait(self):
# #         await asyncio.gather(*self._tasks)
# #         return self._results
    
# #     @staticmethod
# #     def wait(queue: 'APICallQueue'):
# #         async def wait_async():
# #             return await queue.wait()
# #         return asyncio.run(wait_async())

# # @singleton
# # class APICallQueueSingleton(APICallQueue):
# #     pass

# # @singleton
# # class APICallQueueMonitor:
# #     def __init__(self):
# #         self._active_queues = dict()
# #         self._lock = asyncio.Lock()

# #     def add_queue(self, queue: APICallQueue) -> str:
# #         with self._lock:
# #             queue_id = uuid.uuid4()
# #             self._active_queues[queue_id] = queue
# #         return queue_id

# #     def remove_queue(self, queue_id: str):
# #         with self._lock:
# #             self._active_queues.pop(queue_id)

# #     async def stop_all(self):
# #         async with self._lock:
# #             for _, queue in self._active_queues.items():
# #                 await queue.stop()








# import asyncio
# import concurrent.futures
# import threading
# import uuid
# import random
# from functools import partial

# from gptwntranslator.helpers.design_patterns_helper import singleton
# from gptwntranslator.helpers.logger_helper import CustomLogger

# logger = CustomLogger(__name__)

# import asyncio
# import concurrent.futures
# import threading
# import uuid
# import random
# from functools import partial

# @singleton
# class MultiAPICallQueue:
#     def __init__(self):
#         self._active_queues = {}
#         self._lock = threading.Lock()

#     def create_queue(self, num_workers=4):
#         queue_id = uuid.uuid4()
#         queue = APICallQueue(queue_id, self, num_workers=num_workers)
#         with self._lock:
#             self._active_queues[queue_id] = queue
#         return queue_id

#     def add_call(self, queue_id, func, retries=3, **params):
#         with self._lock:
#             queue = self._active_queues[queue_id]
#         return queue.add_call(func, retries, **params)

#     def wait(self, queue_id):
#         with self._lock:
#             queue = self._active_queues[queue_id]
#         return asyncio.run(queue.wait())

#     def stop_queue(self, queue_id):
#         with self._lock:
#             queue = self._active_queues.pop(queue_id)
#         queue.stop()

#     def stop_all(self):
#         with self._lock:
#             for _, queue in self._active_queues.items():
#                 queue.stop()


# class APICallQueue:
#     def __init__(self, queue_id, manager, num_workers=4):
#         self._queue_id = queue_id
#         self._manager = manager
#         self._initialize(num_workers)

#     def _initialize(self, num_workers):
#         self._tasks = []
#         self._results = {}
#         self._futures = []  # Initialize _futures list
#         self._task_lock = asyncio.Lock()
#         self._num_workers = num_workers

#         self._loop = asyncio.new_event_loop()
#         self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self._num_workers)

#         self._thread = threading.Thread(target=self._loop.run_forever)
#         self._thread.start()

#     def add_call(self, func, retries=3, **params):
#         logger.info(f"Adding API call to queue with id: {self._queue_id}, func: {func.__name__}")
#         task_id = uuid.uuid4()
#         future = self._loop.run_in_executor(self._executor, partial(self._execute_call, task_id, func, params, retries))
#         self._tasks.append(future)
#         self._futures.append(future)  # Add future to _futures list
#         return task_id

#     async def _execute_call(self, task_id, func, params, retries):
#         try:
#             logger.info(f"Executing API call in queue with id: {self._queue_id}, task: {task_id}, func: {func.__name__}")
#             func_with_params = partial(func, **params)
#             if asyncio.iscoroutinefunction(func):
#                 result = await func(**params)
#             else:
#                 result = await asyncio.to_thread(func_with_params)
#             logger.info(f"API call in queue with id: {self._queue_id}, task: {task_id}, func: {func.__name__} succeeded. Result: {result}")
#             await self._handle_result(task_id, result)
#         except Exception as e:
#             if retries > 0:
#                 backoff_time = self._exponential_backoff(retries)
#                 logger.info(f"API call in queue with id: {self._queue_id}, task: {task_id}, func: {func.__name__} failed, retrying in {backoff_time} seconds")
#                 await asyncio.sleep(backoff_time)
#                 await self._execute_call(task_id, func, params, retries - 1)
#             else:
#                 logger.error(f"API call in queue with id: {self._queue_id}, task: {task_id}, func: {func.__name__} failed")
#                 await self._handle_result(task_id, e)

#     async def _handle_result(self, task_id, result):
#         if isinstance(result, asyncio.Task):
#             logger.error(f"API call in queue with id: {self._id}, task: {task_id} returned a Task object instead of a result or exception")
#             return

#         async with self._task_lock:
#             self._results[task_id] = result

#     def _exponential_backoff(self, retries_left):
#         max_retries = 3
#         exp_base = 2
#         sleep_time = exp_base ** (max_retries - retries_left) + random.uniform(0, 0.1)
#         return sleep_time

#     async def wait(self):
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             loop = asyncio.get_event_loop()
#             tasks = [loop.run_in_executor(executor, self._get_result, future) for future in self._tasks]

#             for future in asyncio.as_completed(tasks):
#                 task_id = tasks.index(await future)
#                 result = await tasks[task_id]
#                 self._results[task_id] = result
#         return self._results

#     def _get_result(self, future):
#         return future.result()
    
#     def stop(self):
#         logger.debug(f"Stopping API call queue with id: {self._queue_id}")
#         for task in self._tasks:
#             task.cancel()
#         self._executor.shutdown(wait=False)
#         self._loop.call_soon_threadsafe(self._loop.stop)
#         self._thread.join()
#         self._loop.close()

#     @property
#     def loop(self):
#         return self._loop


import asyncio
import concurrent.futures
import threading
import uuid
from functools import partial

from gptwntranslator.helpers.logger_helper import CustomLogger


logger = CustomLogger(__name__)

class MultiAPICallQueue:
    def __init__(self):
        self._active_queues = {}
        self._lock = threading.Lock()

    def create_queue(self, num_workers=4):
        queue_id = uuid.uuid4()
        queue = APICallQueue(queue_id, self, num_workers=num_workers)
        with self._lock:
            self._active_queues[queue_id] = queue
        return queue_id

    def add_call(self, queue_id, func, retries=3, **params):
        with self._lock:
            queue = self._active_queues[queue_id]
        return queue.add_call(func, retries, **params)

    async def wait(self, queue_id):
        with self._lock:
            queue = self._active_queues[queue_id]
        return await queue.wait()

    def stop_queue(self, queue_id):
        with self._lock:
            queue = self._active_queues.pop(queue_id)
        queue.stop()

    def stop_all(self):
        with self._lock:
            for _, queue in self._active_queues.items():
                queue.stop()
                
    def wait_sync(self, queue_id):
        logger.info(f"Waiting for API call queue with id: {queue_id} to finish")
        with self._lock:
            queue = self._active_queues[queue_id]

        async def wait_async():
            return await queue.wait()

        loop = queue._loop
        future = asyncio.run_coroutine_threadsafe(wait_async(), loop)
        result = future.result()
        return result


class APICallQueue:
    def __init__(self, queue_id, manager, num_workers=4):
        self._queue_id = queue_id
        self._manager = manager
        self._loop = asyncio.new_event_loop()
        self._initialize(num_workers)

    def _initialize(self, num_workers):
        self._tasks = []
        self._results = {}
        self._task_lock = asyncio.Lock()
        self._num_workers = num_workers
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self._num_workers)

    def add_call(self, func, retries=3, **params):
        logger.info(f"Adding API call to queue with id: {self._queue_id}, func: {func.__name__}")
        task_id = uuid.uuid4()
        if not self._loop.is_running():
            threading.Thread(target=self._loop.run_forever, daemon=True).start()
        future = self._loop.run_in_executor(self._executor, partial(self._execute_call, task_id, func, params, retries))
        self._tasks.append((task_id, future))
        return task_id

    def _execute_call(self, task_id, func, params, retries):
        async def call_and_handle():
            for attempt in range(retries + 1):
                try:
                    logger.info(f"Starting API call in queue with id: {self._queue_id}, task: {task_id}, func: {func.__name__}")
                    func_with_params = partial(func, **params)
                    if asyncio.iscoroutinefunction(func):
                        result = await func(**params)
                    else:
                        result = func_with_params()
                    logger.info(f"API call in queue with id: {self._queue_id}, task: {task_id}, func: {func.__name__} succeeded. Result: {result}")
                    await self._handle_result(task_id, result)
                except Exception as e:
                    if retries > 0:
                        backoff_time = self._exponential_backoff(retries)
                        logger.info(f"API call in queue with id: {self._queue_id}, task: {task_id}, func: {func.__name__} failed, retrying in {backoff_time} seconds")
                        await asyncio.sleep(backoff_time)
                    else:
                        logger.error(f"API call in queue with id: {self._queue_id}, task: {task_id}, func: {func.__name__} failed. Error: {str(e)}")
                        await self._handle_result(task_id, e)

        self._loop.call_soon_threadsafe(lambda: asyncio.create_task(call_and_handle()))
    
    async def _handle_result(self, task_id, result):
        async with self._task_lock:
            self._results[task_id] = result

    async def wait(self):
        logger.info(f"Waiting for API call queue with id: {self._queue_id} to finish")
        for task_id, future in self._tasks:
            await asyncio.wrap_future(future, loop=self._loop)
        return self._results

    def stop(self):
        for _, future in self._tasks:
            future.cancel()
        self._executor.shutdown(wait=False)
        self._loop.call_soon_threadsafe(self._loop.stop)
