from ..models import db 
from ..models.team_model import Team 
from ..models.user_model import User 
from ..models.task_model import Task 
from sqlalchemy.orm import aliased 
from ..models.association import team_member_association, assignment_association
from sqlalchemy import select 
from ..controllers.parsers import create_new_team_parser
from ..utils import getImageUrl 
import cloudinary.uploader 

# Ham kiem tra the loai member 
def isMember(user_id, team_id):
    stmt = select(team_member_association).where(team_member_association.c.user_id == user_id, team_member_association.c.team_id == team_id)
    
    result = db.session.execute(stmt).first

    if(result): return True
    return False

def isViceLeader(user_id, team_id):
    vice_leader_id = db.session.query(Team.vice_leader_id).filter(Team.id == team_id).first() 
    if(vice_leader_id[0] == user_id): return True
    return False

def isLeader(user_id, team_id):
    leader_id = db.session.query(Team.leader_id).filter(Team.id == team_id).first() 
    print(leader_id) 
    if(leader_id[0] == user_id): return True
    return False

def getRole(userID , teamID): 
    if isViceLeader(userID , teamID) == True: 
        return "vice-leader" 
    if isLeader(userID , teamID) == True: 
        return "leader" 
    return "member" 

# [GET]
def getTeams(): 
    datas = db.session.query(Team).all() 
    response_data = [data.to_dict() for data in datas] 
    return {
        "success": True, 
        "data": response_data # Chinh nhu the nay an toan hon 
    }

def getTeamByID(id): 
    Leader = aliased(User) 
    ViceLeader = aliased(User) 
    
    teamInfo = db.session.query(Team , Leader , ViceLeader).join(Leader , Leader.id == Team.id).join(ViceLeader , ViceLeader.id == Team.id).filter(Team.id == id).first() 
    
    leader_data = teamInfo[1].to_dict() 
    vice_leader_data = teamInfo[2].to_dict() 
    team_data = teamInfo[0].to_dict() 
    
    users = db.session.query(User).join(team_member_association , team_member_association.c.user_id == User.id).filter(team_member_association.c.team_id == id).all() 
    
    user_data = [user.to_dict() for user in users] 
    for i in range(len(user_data)): 
        user_data[i]['role'] = getRole(user_data[i]['id'] , id)
    
    tasks = db.session.query(Task).filter(Task.team_id == id).all() 
    task_data = [task.to_dict() for task in tasks] 
    for i in range(len(task_data)): task_data[i]['dueTime'] = str(task_data[i]['dueTime'])
    response_data = {
        "success": True, 
        "data": team_data, 
        "leader": leader_data, 
        "viceLeader": vice_leader_data, 
        "members": user_data, 
        "tasks": task_data 
    }
    print('Thong tin: ' , response_data) 
    return response_data 
        
# [POST] 
def uploadTeamImage(team , file = '' , url = '' , type = 'icon'): 
    if (file and team): 
        if type == 'icon': 
            if team.icon_url: 
                cloudinary.uploader.destroy(team.icon_url) 
            upload_result = cloudinary.uploader.upload(file) 
            team.icon_url = upload_result['public_id'] 
            return upload_result['secure_url']
        if type == 'banner': 
            if team.banner_url:
                cloudinary.uploader.destroy(team.banner_url) 
            upload_result = cloudinary.uploader.upload(file) 
            team.banner_url = upload_result['public_id']
            return upload_result['secure_url']
                
def update_team(id , data): 
    data = dict(data) 
    if len(list(data.keys())) == 1: 
        return {
            "success": True, 
            "message": "Your team has been updated successfully"
        }
    icon = data.get('icon')  
    banner = data.get('banner') 
    description = data.get('teamDescription')
    leaderID = data.get('leaderID')
    viceLeaderID = data.get('viceLeaderID')
    response_data = {
        "teamID": id 
    }
    team = db.session.query(Team).filter(Team.id == id).first() 
    if icon is not None: 
        iconUrl = uploadTeamImage(team , icon , 'icon') 
        response_data["iconUrl"] = iconUrl 
    if banner is not None: 
        bannerUrl = uploadTeamImage(team , banner , 'banner') 
        response_data["bannerUrl"] = bannerUrl 
    if description is not None: 
        team.description = description 
        response_data["description"] = description
    if leaderID is not None: 
        leader = db.session.query(User).filter(User.id == leaderID).first() 
        team.leader_id = leaderID 
        team.leader = leader 
        response_data["leaderID"] = leaderID 
    if viceLeaderID is not None: 
        viceLeader = db.session.query(User).filter(User.id == viceLeaderID).first() 
        team.vice_leader_id = viceLeaderID 
        team.vice_leader = viceLeader  
        response_data["viceLeaderID"] = viceLeaderID 
    db.session.commit()  
    return {
        "success": True, 
        "message": "Your team has been updated successfully", 
        "data": response_data
    }

def dropImage(id): 
    cloudinary.uploader.destroy(id)     
def delete_team(id): 
    team = db.session.query(Team).filter(id == Team.id).first() 
    tasks = db.session.query(Task).filter(Task.team_id == id).all() 
    
    # Xoa du lieu cho db.Table, khong phai 1 class 
    db.session.query(assignment_association).filter(assignment_association.c.task_id.in_([t.id for t in tasks])).delete(synchronize_session=False) 
    
    db.session.query(team_member_association).filter(team_member_association.c.team_id == id).delete(synchronize_session=False) 
    
    for x in tasks: 
        db.session.delete(x) 
    db.session.delete(team) 
    db.session.commit() 
    return {
        "success": True, 
        "message": "Your team has been deleted successfully"
    }
    
    
        
            
    
    