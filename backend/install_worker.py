import json
from pathlib import Path
from pprint import pprint
import queue
import signal
import sys
from hytils import lightgreen, purple, red, yellow
from logger import slog
from messages import WorkerCommand, WorkerResponse
import multiprocessing as mp
from typing import Literal

try:
    from hinstall import __version__
except:
    dev_dir: str = str(Path(__file__).resolve().parent.parent.parent / "hinstall")
    slog.warning(f"Import from dev directory: {dev_dir}")
    sys.path.append(dev_dir)

try:
    from hinstall import (
        ExtPackages,
        PyPackages,
        download_install_ext_packages,
        g_backend_dirs,
        generate_backend_env,
        get_python_version,
        parse_packages_toml_,
        get_pypackage_list,
        get_pip_versions,
    )
except Exception as e:
    slog.critical(f"Failed to import hinstall package: {str(e)}")


InstallWorkerTask = Literal[
    'shutdown',
    'packages_cfg'
]
worker_task_list = list(InstallWorkerTask.__args__)



class InstallWorker(mp.Process):
    """Worker process that executes long-running tasks"""
    def __init__(
        self,
        task_queue: mp.Queue,
        result_queue: mp.Queue,
        stop_event: mp.Event
    ):
        super().__init__()
        self.task_queue: mp.Queue = task_queue
        self.result_queue: mp.Queue = result_queue
        self.stop_event: mp.Event = stop_event



    def run(self):
        # Ignore KeyboardInterrupt inside the worker
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        slog.info(purple(f"[{self.pid}] ℹ️  worker process started"))

        while not self.stop_event.is_set():

            try:
                msg: dict = self.task_queue.get(timeout=0.2)
                task_name: InstallWorkerTask = msg['cmd']
                payload: dict | None = msg.get('payload', {})

                # Route to appropriate task handler
                if task_name == 'shutdown':
                    slog.info(purple(f"[{self.pid}] ℹ️  received shutdown"))
                    break

                elif task_name == 'install':
                    # if 'hinstall' not in sys.modules:
                    #     try:
                    #         from hinstall import (
                    #             ExtPackages,
                    #             PyPackages,
                    #             download_install_ext_packages,
                    #             g_backend_dirs,
                    #             generate_backend_env,
                    #             get_python_version,
                    #             parse_packages_toml_,
                    #             get_pypackage_list,
                    #             get_pip_versions,
                    #         )
                    #     except Exception as e:
                    #         slog.critical("Failed to import hinstall package")

                    slog.info(purple(f"[{self.pid}] parse {payload}"))
                    self.handle_parse_cfg(payload)


                # else:
                #     self.send_result(
                #         WorkerResponse(
                #             type="error",
                #             payload=f"Unknown task: {task_name}"
                #         )
                #     )

            except queue.Empty:
                continue

            except Exception as e:
                print(purple(f"[{self.pid}] ❌ uncaught exception: {str(e)}"))
                self.send_result(
                    WorkerResponse(
                        type="exception",
                        payload=f"exception: {str(e)}"
                    )
                )

        slog.info(purple(f"[{self.pid}] ℹ️ terminated"))



    def do_stop(self) -> bool:
        """Check if task should stop"""
        return self.stop_event.is_set()


    def send_result(self, response: WorkerResponse):
        """Send result back to server"""
        self.result_queue.put(response)


    def get_rehost_dir(self, company: str = "herlegon") -> Path:
        local_package_dir: Path

        if sys.platform == "win32":
            local_package_dir = Path("A:\\") / company / "rehost"

        elif sys.platform == "linux":
            local_package_dir = Path("/opt") / company / "rehost"

        elif sys.platform == "darwin":
            local_package_dir = Path.home() / company / "rehost"

        return local_package_dir



    def handle_parse_cfg(self, payload: dict) -> None:
        print(type(payload))
        pprint(payload)
        toml_cfg = json.loads(payload.get("cfg"))

        product_name: str = payload.get("product", "hconvert")
        reinstall: bool = payload.get("reinstall", False)
        use_local_host: bool = payload.get("use_local_host", False)
        local_host: str = payload.get("local_host", "")


        packages_cfg = parse_packages_toml_(toml_cfg)
        # try:
        #     packages_cfg = parse_packages_toml_(payload)
        # except Exception as e:
        #     exception: str = str(e)
        #     self.send_result(
        #         WorkerResponse(type="exception", payload=exception)
        #     )
        #     return

        self.send_result(
            WorkerResponse(
                type="install",
                payload={
                    'type': "cfg",
                    'state': "parsed",
                }
            )
        )

        # for testing purpose
        if use_local_host:
            g_backend_dirs.local_host = local_host if local_host else self.get_rehost_dir()

        # All packages except python
        ext_packages = ExtPackages(packages_cfg, sys.platform)
        packages_to_install = ext_packages.get_all_except('python')

        # Install external packages
        if packages_to_install:
            installed: bool = download_install_ext_packages(
                packages=packages_to_install,
                reinstall=reinstall,
                threads=1,
                use_local_host=use_local_host
            )
            if installed:
                print(lightgreen("All packages installed"))
            else:
                print(red("Error: missing package(s)"))
        else:
            print(lightgreen("No packages to install"))

        self.send_result(
            WorkerResponse(
                type="install",
                payload={
                    'type': "external",
                    'state': "installed",
                }
            )
        )

        # Install python packages
        # g_backend_dirs.python_exe = ""
        backend_env = generate_backend_env()

        # Get python packages that have to be installed first
        py_packages = PyPackages(packages_cfg, sys.platform)
        py_packages = py_packages.get_initial()

        pprint(py_packages)

        pprint(g_backend_dirs)

        print(get_python_version())

        result = get_pypackage_list()


        # update_package_info(py_packages[0])

        installed_versions = get_pip_versions()
        pprint(installed_versions)
