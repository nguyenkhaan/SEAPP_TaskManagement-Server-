from flask_jwt_extended import decode_token


def decode_jwt_token(token): 
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        if not payload.get('email_verified'):   #Phai veriy email thi moi cho trich xuat thong tin tu token 
            return None 
        email = payload.get('email') 
        password_hash = payload.get('password_hash')
        name = payload.get('name') 
        return {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "user_id": idinfo.get("sub")  # Google unique user id
        }
    except jwt.ExpiredSignatureError:
        print(f"Token het han")
        return None
    except jwt.InvalidTokenError:
        print(f"Token loi gia tri")
        return None
    except Exception as e:
        print(f"Lỗi giải mã token: {e}")
        return None      



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
    except Exception as e:
        print(f"Lỗi giải mã token: {e}")
        return None       