from contextlib import contextmanager

from django.core.cache import cache


@contextmanager
def acquire_thread_safe_lock(lock_id, timeout=10):
    lock = cache.lock(lock_id, timeout=timeout)
    have_lock = lock.acquire(blocking=True)
    try:
        yield have_lock
    finally:
        if have_lock:
            lock.release()
