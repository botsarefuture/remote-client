def retry_on_failure(max_retries=5, backoff_factor=0.5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.ConnectionError:
                    retries += 1
                    time.sleep(backoff_factor * (2 ** retries))
                    if retries == max_retries:
                        raise
        return wrapper
    return decorator