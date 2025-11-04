import asyncio, json, logging, time
from multiprocessing import Process, Queue

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

HEARTBEAT_TIMEOUT = 12.0

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    logging.info(f"Client connected: {addr}")
    last_ping = time.time()
    task_proc = None
    task_queue = None

    async def send(obj):
        data = json.dumps(obj) + "\n"
        writer.write(data.encode())
        await writer.drain()

    async def watch_worker(task_id):
        nonlocal task_proc, task_queue
        while True:
            await asyncio.sleep(0.5)
            if task_proc is None:
                return
            if not task_proc.is_alive():
                try:
                    if not task_queue.empty():
                        out = task_queue.get_nowait()
                        await send({"type":"result","id":task_id, **out})
                    else:
                        await send({"type":"result","id":task_id,"status":"error","error":"worker died"})
                except Exception as e:
                    await send({"type":"result","id":task_id,"status":"error","error":str(e)})
                task_proc = None
                task_queue = None
                return

    def start_task(task_id, filepath, settings):
        nonlocal task_proc, task_queue
        from time import sleep
        import traceback
        from multiprocessing import Queue

        def long_job(q_out, filepath, settings):
            try:
                d = settings.get("duration", 10)
                t0 = time.time()
                logging.info(f"Worker: starting heavy work {filepath} for {d}s")
                end = t0 + d
                while time.time() < end:
                    _ = sum(i*i for i in range(1000))
                    sleep(0.01)
                q_out.put({"status":"ok","result":{"file":filepath,"elapsed":time.time()-t0}})
            except Exception:
                q_out.put({"status":"error","error":traceback.format_exc()})

        if task_proc and task_proc.is_alive():
            return {"status":"error","error":"another task running"}
        task_queue = Queue()
        task_proc = Process(target=long_job, args=(task_queue, filepath, settings))
        task_proc.start()
        asyncio.create_task(watch_worker(task_id))
        return {"status":"ok","message":"task started"}

    async def heartbeat_monitor():
        while True:
            await asyncio.sleep(1)
            if time.time() - last_ping > HEARTBEAT_TIMEOUT:
                logging.error("No heartbeat for %.1fs; closing connection.", time.time()-last_ping)
                writer.close()
                await writer.wait_closed()
                return

    asyncio.create_task(heartbeat_monitor())

    try:
        async for line_bytes in reader:
            line = line_bytes.decode().strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception:
                logging.error("Invalid JSON: %s", line)
                continue
            cmd = msg.get("cmd")
            if cmd == "heartbeat":
                last_ping = time.time()
                await send({"type":"pong"})
            elif cmd == "start_task":
                r = start_task(msg.get("id"), msg.get("filepath"), msg.get("settings", {}))
                await send({"type":"info", **r})
            elif cmd == "kill_task":
                if task_proc and task_proc.is_alive():
                    task_proc.terminate()
                    await send({"type":"info","message":"task killed"})
            elif cmd == "quit":
                await send({"type":"info","message":"bye"})
                writer.close()
                await writer.wait_closed()
                return
            else:
                await send({"type":"error","message":f"unknown cmd {cmd}"})
    except asyncio.CancelledError:
        pass
    finally:
        logging.info(f"Client disconnected: {addr}")

async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8765)
    addrs = ", ".join(str(s.getsockname()) for s in server.sockets)
    logging.info(f"Backend listening on {addrs}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
