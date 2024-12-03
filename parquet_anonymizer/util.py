import random
import string

DEFAULT_KEY_FILE = "anonymizer.key"


def keygen():
    """Generate random alphanumeric key of length 15"""
    with open(DEFAULT_KEY_FILE, "w") as key_file:
        key = "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(15)
        )
        key_file.write(key)
