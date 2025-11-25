from ..models import db 
from ..models.team_model import Team 
from ..models.user_model import User 
from ..models.task_model import Task 
from sqlalchemy.orm import aliased 
from ..models.association import team_member_association, assignment_association
from sqlalchemy import select 

def isMember(user_id, team_id):
    stmt = select(team_member_association).where(team_member_association.c.user_id == user_id, team_member_association.c.team_id == team_id)
    
    result = db.session.execute(stmt).first

    if(result): return True
    return False

def isViceLeader(user_id, team_id):
    team = Team.query.get(team_id)
    vice_leader_id = team.get('vice_leader_id')
    if(vice_leader_id == user_id): return True
    return False

def isLeader(user_id, team_id):
    team = Team.query.get(team_id)
    leader_id = team.get('leader_id')
    if(leader_id == user_id): return True
    return False

def getTeams(): 
    datas = db.session.query(Team).all() 
    datas = [data.to_dict() for data in datas] 
    response_data = [
        {
            "teamID": dt["teamID"], 
            "iconUrl": dt["iconUrl"],  
            "teamName": dt["name"], 
            "teamDescription": dt["teamDescription"] 
        }
        for dt in datas 
    ]
    return {
        "success": True, 
        "data": response_data 
    }
def getTeamByID(id): 
        Leader = aliased(User) 
        ViceLeader = aliased(User) 
        teamInfo = db.session.query(Team , Leader , ViceLeader).join(Team , Team.leader_id == Leader.id).join(ViceLeader , ViceLeader.id == Team.vice_leader_id).filter(id == Team.id).first() 
        # Lay thong tin ve members 
        members = db.session.query(User).join(team_member_association , User.id == team_member_association.c.user_id).filter(team_member_association.c.team_id == id).all() 
        members = [member.to_dict() for member in members] 
        # Lay thong tin ve tasks 
        tasks = teamInfo[0].to_dict()['tasks']
        tasks = [task.to_dict() for task in tasks]
        for i in range(len(tasks)): tasks[i]['dueTime'] = str(tasks[i]['dueTime'])
        return {
            "success": True, 
            "data": {
                "teamID": teamInfo[0].id, 
                "iconUrl": teamInfo[0].icon_url, 
                "bannerUrl": teamInfo[0].banner_url, 
                "teamName": teamInfo[0].name, 
                "teamDescription": teamInfo[0].description 
            }, 
            "leader": {
                "userID": teamInfo[1].id, 
                "name": teamInfo[1].name, 
                "avatarUrl": teamInfo[1].avatar_url
            }, 
            "viceLeader": {
                "userID": teamInfo[2].id, 
                "name": teamInfo[2].name, 
                "avatar": teamInfo[2].avatar_url
            }, 
            "memebers": members, 
            "tasks": tasks 
        }, 200 
def createTeam(): 
    return True 