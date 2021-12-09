import time
import jwt

jwt_secret = '336215407d0ca400fecdf873c090345accd53ce976e705f8ed6a71492c8394c2'
jwt_algorithm = 'HS256'


def create_access_token(user_email: str):
    payload = {
        "user_email": user_email,
        "expires": time.time() + 6000
    }
    encoded_token = jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)
    return {
        "access_token": encoded_token
    }


def decode_token(encoded_token: str):
    try:
        decoded_token = jwt.decode(encoded_token, jwt_secret, algorithms=[jwt_algorithm])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
