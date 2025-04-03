print("[INIT] Util")

import time

def wait(ms):
    t = time.time()
    while (time.time()-t) < ms/1000:
        pass
    return True