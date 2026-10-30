import functools

def test_scenario(scenario:str):
    """A decorator factory that accepts a custom message."""

    def decorator(func):
        @functools.wraps(func)  # Preserves the original function's metadata
        def wrapper(*args, **kwargs):
            # 1. Print your custom test message/text
            print(f"Scenario: {scenario}")

            # 2. Execute the actual function and capture its result
            result = func(*args, **kwargs)

            # 3. Return the result so the function behaves normally
            return result

        return wrapper

    return decorator