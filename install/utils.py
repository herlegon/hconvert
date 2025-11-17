from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

PLATFORMS: tuple[str] = ('win32', 'linux', 'darwin')

def check_site_reachable(url: str, max_retries: int = 3):
    """Check if site is reachable with retries"""
    for attempt in range(max_retries):
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            urlopen(req, timeout=5)
            return True
        except (URLError, HTTPError):
            if attempt < max_retries - 1:
                continue
    return False




if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    from logger import ilog
    ilog.setLevel("DEBUG")

    reachable = check_site_reachable(url="github.com")
