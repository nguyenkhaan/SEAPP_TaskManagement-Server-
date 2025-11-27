from flask import Response 
from flask_restful import Api, Resource 
from flask import Blueprint
from ..services.teams_service import getTeams, getTeamByID, uploadTeamImage
from ..models.team_model import Team 
from ..models.user_model import User 
from ..models import db 
from .parsers import create_new_team_parser
from .parsers import update_team_parser 
from ..services.teams_service import update_team, delete_team
from ..services.teams_service import generate_team_code, join_code
from flask import request 
# Phai import theo kieu relative path ntn, bo dau . o dau di thi se thanh absolute path 

team_bp = Blueprint('team' , __name__) 
team_api = Api(team_bp) 

class Teams(Resource): 
    def get(self, id = None): # Viet 1 ham thoi, khong duoc phep co 2 ham 
        #cung ten trong Python, du cho khac danh sach tham so 
        if id is None: 
            response_data = getTeams() 
            print(response_data) 
            return response_data , 200 
        else: 
            response_data = getTeamByID(id) 
            return response_data , 200 
    def post(self): 
        data = dict(create_new_team_parser.parse_args()) 
        leader_id = data.get('userID') 
        name = data.get('teamName') 
        icon = data.get('icon') 
        banner = data.get('banner') 
        description = data.get('teamDescription')

        new_team = Team() 
        new_team.name = name 
        new_team.description = description 
        new_team.leader_id = leader_id 
        # Thuc hien update leader 
        leader = db.session.query(User).filter(User.id == leader_id).first() 
        new_team.leader = leader 
        new_team.icon_url = None 
        new_team.banner_url = None 
    
    
        if icon is not None: 
            # Thuc hien viec update du lieu len cloudinary 
            url = uploadTeamImage(new_team , icon , 'icon')
            new_team.icon_url = url 
        else: 
            new_team.icon_url = None 
        if banner is not None: 
            # Thuc hien update du lieu len cloudinary 
            url = uploadTeamImage(new_team , banner , 'banner') 
            new_team.icon_url = url 
        else: 
            new_team.banner_url = '' 


        db.session.add(new_team) 
        db.session.commit() 
        
        return {
            "success": True, 
            "message": "Your team has been created successfully", 
            "data": new_team.to_dict(), 
            "leader": leader.to_dict() 
        }, 201 
    def put(self, id = None): 
        data = update_team_parser.parse_args() 
        if id is None: 
            return {
                "success": True, 
                "message": "Don't know team to update"
            } , 405 
        response_data = update_team(id , data) 
        return response_data
    def delete(self , id): 
        response_data = delete_team(id) 
        return response_data , 200 

class TeamJoinCode(Resource): 
    def post(self, id): 
        time = request.json.get('expiresIn')
        if time is not None: 
            response_data = generate_team_code(id , time) 
            return response_data , 201 
        return {
            "Success": False, 
            "message": "Cannot create a team code"
        }

class TeamJoin(Resource): 
    def post(self): 
        data = request.json 
        if data.get('userID') and data.get('code'): 
            code = data.get('code') 
            userID = data.get('userID') 
            response_data = join_code(code , userID) 
            return response_data , 200
        return {
            "success": False, 
            "message": "Invalid information"
        }
        
team_api.add_resource(Teams , '/' , '/<int:id>')
team_api.add_resource(TeamJoinCode , '/<int:id>/join-code')
team_api.add_resource(TeamJoin , '/join')
        