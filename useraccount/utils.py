import random
import string

def generate_otp(length = 6):
    character = string.digits
    otp = "".join(random.choice(character) for _ in range(length))
    return otp
