import subprocess
import time

class Client:
    def __init__(self, client_path, auth_ticket, join_script_url,
                 browser_tracker_id, locale):
        self.client_path = client_path
        self.auth_ticket = auth_ticket
        self.join_script_url = join_script_url
        self.browser_tracker_id = browser_tracker_id
        self.locale = locale
        self._process = None

    def __del__(self):
        self.close()
        super().__init__()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *_):
        self.close()

    @property
    def pid(self):
        if self._process:
            return self._process.pid

    def start(self):
        """Launches client process."""
        if self._process:
            return

        self._process = subprocess.Popen([
            self.client_path,
            "-t", self.auth_ticket,
            "-j", self.join_script_url,
            "-b", self.browser_tracker_id,
            f"--launchtime={time.time()*1000:0.0f}",
            "--rloc", self.locale,
            "--gloc", self.locale
        ])

    def wait(self, timeout=None):
        """Blocks until client process is closed."""
        self._process.wait(timeout)

    def close(self, force=False):
        """Terminates client process."""
        if not self._process:
            return
            
        if force:
            self._process.kill()
        else:
            self._process.terminate()
            
