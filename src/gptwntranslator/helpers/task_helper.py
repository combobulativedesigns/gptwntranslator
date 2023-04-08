from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import uuid

from gptwntranslator.helpers.logger_helper import CustomLogger


logger = CustomLogger(__name__)

class Task:
    def __init__(self, max_workers, retry_on_exceptions=(), max_retries=3):
        self.max_workers = max_workers
        self.retry_on_exceptions = retry_on_exceptions
        self.max_retries = max_retries
        self.subtasks = []
        logger.info(f'Created task with max_workers={max_workers}, retry_on_exceptions={retry_on_exceptions}, max_retries={max_retries}')

    def add_subtask(self, subtask_func, *args, **kwargs):
        subtask = Task(self.max_workers)
        subtask.id = uuid.uuid4()
        subtask.task_func = subtask_func
        subtask.args = args
        subtask.kwargs = kwargs
        self.subtasks.append(subtask)
        logger.info(f'Added subtask {subtask.id} to task')
        return subtask.id

    def run_subtasks(self):
        logger.info(f'Running subtasks of task')
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._run_subtask_with_retry, subtask): subtask for subtask in self.subtasks}
            results = {}
            for future in as_completed(futures):
                subtask = futures[future]
                try:
                    logger.info(f'Finished running subtask {subtask.id}')
                    results[subtask.id] = future.result()
                except Exception as e:
                    results[subtask.id] = e
                    logger.error(f'Exception occurred while running subtask {subtask.id}: {e}')
        return results

    def _run_subtask_with_retry(self, subtask):
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f'Running subtask {subtask.id}')
                return subtask.task_func(*subtask.args, **subtask.kwargs)
            except self.retry_on_exceptions as e:
                logger.warning(f'Exception occurred while running subtask {subtask.id}: {e}')
                if attempt == self.max_retries:
                    raise
                sleep_duration = 2 ** attempt
                time.sleep(sleep_duration)