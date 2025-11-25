from flask import Response 
from flask_restful import Api, Resource 
from flask import Blueprint
from ..services.teams_service import getTeams, getTeamByID 
team_bp = Blueprint('team' , __name__) 
team_api = Api(team_bp) 

class Teams(Resource): 
    def get(self, id = None): 
        if id == None: 
            response_data = getTeams() 
            return response_data , 200
        else:  
            # Lay thong tin ve team 
            response_data = getTeamByID(id) 
            return response_data , 200 
        def post(self): 
            #Tao moi mot team 
            return True 
            

team_api.add_resource(Teams , '/' , '/<int:id>')

        