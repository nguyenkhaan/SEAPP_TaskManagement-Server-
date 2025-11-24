import jwt
from flask import current_app 
from flask_jwt_extended import decode_token

def decode_verification_token(token):
    try:
        payload = decode_token(token)
        email = payload.get('email') 
        password_hash = payload.get('password_hash')
        purpose = payload.get('purpose')

        if purpose != 'email_verification':
            return None

        return {
            'email': email,
            'password_hash': password_hash,
            'name': payload.get('name') 
        }

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception as e:
        print(f"Lỗi giải mã token: {e}")
        return None       


def decode_reset_password_token(token: str):
    try:
        payload = decode_token(token)
        purpose = payload.get('purpose')

        if purpose != 'reset_password':
            return None

        user_id = payload.get('user_id')
        return {
            'user_id': user_id
        }

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception as e:
        print(f"Lỗi giải mã token: {e}")
        return None       

