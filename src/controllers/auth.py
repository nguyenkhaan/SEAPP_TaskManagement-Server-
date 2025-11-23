from flask import Blueprint, url_for, current_app, redirect
from flask_restful import Api, Resource
from .parsers import register_parser, login_parser, verify_parser
from werkzeug.security import generate_password_hash
from ..services.users_service import createUser, getUserByEmail, checkUser, uploadAvatar
from ..services.jwt_service import decode_verification_token
from flask_jwt_extended import create_access_token
import os
from dotenv import load_dotenv 
import secrets
from datetime import timedelta
from flask_mail import Message
from ..config.mail import mail


load_dotenv()
auth_bp = Blueprint('auth', __name__)
auth_api = Api(auth_bp)

class Register(Resource):
    def post(self):
        register_args = register_parser.parse_args()
        name = register_args['name']
        email = register_args['email']

        if(getUserByEmail(email)):
            return {
                "success": "error",
                "message": "Registration failed. The email provided is already in use.",
                "data": None
            }, 409

        password_hash = generate_password_hash(register_args['password'])
        
        custom_claims = {
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "purpose": "email_verification"
        }

        verification_token = create_access_token(identity=email, additional_claims=custom_claims, expires_delta=timedelta(hours=24))

        verify_url = url_for('auth.verify', _external=True, token = verification_token )


        msg = Message('NoTask email verification', recipients=[email])
        msg.html = f"""<div class="header">
            <h1>Welcome to NoTask!</h1>
        </div>
        <div class="content">
            <p>Hi {name},</p>
            <p>Thank you for registering with NoTask, your ultimate task management solution. To complete your registration and start managing your tasks efficiently, please verify your email address by clicking the button below:</p>
            <div class="button-container">
                <a href="{verify_url}" class="button">Verify My Email</a>
            </div>
            <p>This link will expire in 24 hours. If you did not sign up for NoTask, please ignore this email.</p>
            <p>Best regards,</p>
            <p>The NoTask Team</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 NoTask. All rights reserved.</p>
            <p>NoTask - Your simple solution for task management.</p>
            <p><a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a></p>
        </div>"""
        mail.send(msg)

        return {
            "message": "Verification email sent. Please check your inbox.", 
            "token": verification_token
            }, 200
        

class Verify(Resource):
    def get(self):
        args = verify_parser.parse_args()
        verification_token = args['token']

        user_data = decode_verification_token(verification_token)
        name = user_data['name']
        email = user_data['email']
        password = user_data['password_hash']

        if(getUserByEmail(email)):
            return redirect(
                f"https://{os.getenv('WEB_URL')}?verified=false", 
                code=302
            )

        new_user = createUser(name, email, password)

        if(new_user):
            access_token = create_access_token(identity=str(new_user['id']))
            
            return redirect(
                f"https://{os.getenv('WEB_URL')}?token={access_token}&verified=true", 
                code=302
            )
        else:
            return redirect(
                f"https://{os.getenv('WEB_URL')}?token={access_token}&verified=false", 
                code=302
            )
    

        
            

class Login(Resource):
    def post(self):
        login_args = login_parser.parse_args()
        email = login_args['email']
        password = login_args['password']

        user = checkUser(email = email, password = password)
        if(user):
            access_token = create_access_token(identity=str(user['id']))
            
            return {
                "success": True,
                "message" : "Login successful.",
                "data": {
                    "user": user
                },
                "tokens": {
                    "access_token": access_token,
                    "token_type": "Bearer", 
                    "expires_in": 60*60*24*7,
                }
            }, 200
        
        return {
            "success": False,
            "message": "Invalid credentials provided.",
            "data": None
        }, 401
    
class LoginGoogle(Resource):
    def get(self):
        try:
            state = secrets.token_urlsafe(32)
            session['oauth_state'] = state
            redirect_uri = url_for('auth.authorizegoogle', _external=True)
            return google.authorize_redirect(redirect_uri, state)
        except Exception as e:
            current_app.logger.error(f"Error during login:{str(e)}")
            return {
                "success": False,
                "message": "Unable to initiate Google login."
            }, 500

class AuthorizeGoogle(Resource):
    def get(self):
        try:
            # Xác thực state token (CSRF protection)
            state = request.args.get('state')
            if not state or state != session.get('oauth_state'):
                    raise Unauthorized("Invalid state parameter")    

            # Xóa state sau khi dùng
            session.pop('oauth_state', None)
                    
            token = google.authorize_access_token()
            if not token:
                raise BadRequest("Failed to obtain access token")
            
            userinfo_endpoint = google.server_metadata['userinfo_endpoint']
            if not userinfo_endpoint:
                raise BadRequest("Userinfo endpoint not available")

            resp = google.get(userinfo_endpoint)
            if resp.status_code != 200:
                raise BadRequest("Failed to fetch user info from Google")

            user_info = resp.json()
            email = user_info['email']

            user = getUserByEmail(email)
            user['login_method'] = 'google'

            if(user):
                access_token = create_access_token(identity=user['id'], additional_claims={'login_method': 'google'})

                return {
                    "success": True,
                    "message" : "Login successful.",
                    "data": {
                        "user": user
                    },
                    "tokens": {
                        "access_token": access_token,
                        "token_type": "Bearer", 
                        "expires_in": 60*60*24*7,
                    }
                }, 200
            
            name = user_info['name']
            picture = user_info['picture']
            sub_id = user_info['sub']
            
            user = createUser(name=name, email=email, password = sub_id)
            uploadAvatar(id=user['id'], url=picture)
            access_token = create_access_token(identity=user['id'], additional_claims={'login_method': 'google'})
            return {
                    "success": True,
                    "message" : "Login successful.",
                    "data": {
                        "user": user
                    },
                    "tokens": {
                        "access_token": access_token,
                        "token_type": "Bearer", 
                        "expires_in": 60*60*24*7,
                    }
                }, 200
        except Unauthorized as e:
            current_app.logger.warning(f"Unauthorized Google login attempt: {str(e)}")
            return {
                "success": False,
                "message": "Unauthorized access."
            }, 401
            
        except BadRequest as e:
            current_app.logger.error(f"Bad request during Google auth: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }, 400
            
        except Exception as e:
            current_app.logger.error(f"Unexpected error during Google auth: {str(e)}")
            return {
                "success": False,
                "message": "An error occurred during login."
            }, 500

            

        

auth_api.add_resource(Register, '/register')
auth_api.add_resource(Verify, '/verify')
auth_api.add_resource(Login, '/login')
auth_api.add_resource(LoginGoogle, '/login-google')
auth_api.add_resource(AuthorizeGoogle, '/authorize-google')