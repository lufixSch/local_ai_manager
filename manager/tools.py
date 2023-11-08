import os
import signal
from typing import Callable, Literal
from subprocess import Popen


class Tool:
    """
    Base class for starting local AI tools
    """

    process: Popen | None = None

    def __init__(
        self,
        location: str,
        venv: str,
        state_publisher: Callable[
            [
                Literal["oobabooga", "automatic1111"],
                Literal["idle", "running", "stopped"] | None,
            ],
            None,
        ] = lambda *args: None,
    ) -> None:
        self.location = location
        self.venv = venv
        self.state_publisher = state_publisher

    def start(self):
        """Start tool as separate process (If a subprocess is already running, it will be terminated first)"""

        if self.process and not self.process.poll():
            print("Stopping previous instance...")
            self.stop()

        cmd = f"source {os.path.join(self.venv, 'bin', 'activate')} && ./webui.sh --listen"

        # Start process with preexec_fn=os.setsid to ensure
        # the manager script does not exit when tool is stopped with os.killpg
        self.process = Popen(cmd, shell=True, cwd=self.location, preexec_fn=os.setsid)

    def stop(self):
        """Stop running process"""

        if not self.process:
            print("No active instance to terminate")
            return

        try:
            # Use killpg to ensure subprocesses are killed too
            os.killpg(os.getpgid(self.process.pid), signal.SIGINT)
            self.process = None
        except Exception as e:
            print(f"Error stopping tool: {e}")


class Oobabooga(Tool):
    """
    Starts the oobabooga webui
    """

    def start(self):
        print("Starting oobabooga...")
        super().start()
        self.state_publisher("oobabooga", "running")

    def stop(self):
        print("Stopping oobabooga...")
        super().stop()
        self.state_publisher("oobabooga", "idle")


class AUTOMATIC1111(Tool):
    """
    Starts the automatic1111 webui
    """

    def start(self):
        print("Starting AUTOMATIC1111...")
        super().start()
        self.state_publisher("automatic1111", "running")

    def stop(self):
        print("Stopping AUTOMATIC1111...")
        super().stop()
        self.state_publisher("automatic1111", "idle")
