

# Persistent small-task worker
import asyncio
import multiprocessing

from worker import nnlib_worker


small_cmd_queue = multiprocessing.Queue()
small_event_queue = multiprocessing.Queue()
small_worker = multiprocessing.Process(
    target=nnlib_worker,
    name="nnlib_worker",
    args=(small_cmd_queue, small_event_queue),
)
small_worker.start()

# Heavy task (spawn on demand)
heavy_process = None
heavy_cmd_queue = None
heavy_event_queue = None


# # Example worker integration (stub)
# async def run_long_task_async(params):
#     # Replace with multiprocessing or ProcessPoolExecutor
#     await asyncio.sleep(8)  # simulate long task
#     return {"status": "done", "params": params}
