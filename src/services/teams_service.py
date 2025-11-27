import datetime
from ..models import db 
from ..models.team_model import Team 
from ..models.user_model import User 
from ..models.task_model import Task 
from sqlalchemy.orm import aliased 
from ..models.association import team_member_association, assignment_association
from sqlalchemy import select, insert
from ..controllers.parsers import create_new_team_parser
from ..models.invite_code_model import InviteCode 
from .randomCode import randomCode 
from .datetime_service import addTime, toStr, getNow
from ..utils import getImageUrl
import cloudinary.uploader 


# Viet lai team service 
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

# Kiem tra co phai user hay khong 
def isUser(id): 
    user_id = db.session.query(1).filter(id == User.id).first() 
    if user_id: return True 
    return False 

def isTeam(id): 
    team = db.session.query(1).filter(id == Team.id).first() 
    if team: return True 
    return False 

def createCode(): 
    code = randomCode(8) 
    exists = db.session.query(1).filter(InviteCode.code == code).first() 
    if exists: 
        code = randomCode(9) 
    return code 

def isUserMember(userID , teamID): 
    # Kiem tra userID nay co phai la thanh vien cua teamID hay khong 
    stmt = select(1).where(
        team_member_association.c.user_id == userID, 
        team_member_association.c.team_id == teamID 
    ) 
    e = db.session.execute(stmt).first() 
    if e: 
        return True 
    return False 

def addMemberToTeam(userID , teamID): 
    stmt = insert(team_member_association).values(
        user_id = userID, 
        team_id = teamID 
    )
    db.session.execute(stmt) 
    db.session.commit() 


def createCodeForTeam(teamID , expise): # Ham dung de tao code cho team 
    
    if not isTeam(teamID): return None # Neu khong co team thi se khong tao group 
    
    code = createCode() 
    new_invite_code = InviteCode()  
    new_invite_code.code = code 
    new_invite_code.time_expired = addTime(datetime=datetime.datetime.now() , second= expise) 
    new_invite_code.team_id = teamID #Bat buoc phai gan lai cai nay 
    invite = db.session.query(InviteCode).filter(InviteCode.team_id == teamID).first() 
    
    if invite: 
        invite.code = code 
        invite.time_expired = addTime(datetime=datetime.datetime.now() , second= expise) 
    else: 
        db.session.add(new_invite_code) 
    db.session.commit() 
    return code 
    

def queryTeam(id): 
    team = db.session.query(Team.id , Team.name , Team.icon_url , Team.banner_url , Team.leader_id , Team.vice_leader_id , Team.description).filter(id == Team.id).first() 
    if team: 
        return {
            "teamID": team[0], 
            "teamName": team[1], 
            "icon": getImageUrl(team[2]), 
            "banner": getImageUrl(team[3]), 
            "leaderID": team[4], 
            "viceLeaderID": team[5], 
            "description": team[6] 
        }
    return None # Khong tim thay team 

# Upload anh len cloudinary danh rieng cho teams 
def uploadTeamImage(team , file = '' , type = 'icon'): 
    if (file and team): 
        if type == 'icon': 
            if team.icon_url: 
                cloudinary.uploader.destroy(team.icon_url) 
            upload_result = cloudinary.uploader.upload(file) 
            team.icon_url = upload_result['public_id'] 
            return upload_result['secure_url']
        else: 
            if team.banner_url:
                cloudinary.uploader.destroy(team.banner_url) 
            upload_result = cloudinary.uploader.upload(file) 
            team.banner_url = upload_result['public_id']
            return upload_result['secure_url']
#Lay thong tin cua team theo id 
def getTeamByID(id): 
    Leader = aliased(User) 
    ViceLeader = aliased(User) 
    
    exists = db.session.query(
        Team.id , Team.name , Team.icon_url , Team.banner_url , Team.description,
        Leader, 
        ViceLeader 
        ).join(Leader , Leader.id == Team.leader_id).outerjoin(ViceLeader , ViceLeader.id == Team.vice_leader_id).filter(Team.id == id).first() 
    
    if not exists: 
        return {
            "success": False, 
            "message": "Team not found"
        } 
    leader = exists[5].to_dict() 
    vice_leader = None 
    if exists[6]: 
        vice_leader = exists[1].to_dict() 
        
    team = {
        "id": exists[0], 
        "name": exists[1], 
        "icon": getImageUrl(str(exists[2])),
        "banner": getImageUrl(str(exists[3])),
        "description": str(exists[4]) 
    }

    users = db.session.query(User).join(team_member_association , team_member_association.c.user_id == User.id).filter(team_member_association.c.team_id == id).all() 
    users = [
        {
        **user.to_dict(),
        "role": "leader" if user.id == leader.get('id')
                else ("vice-leader" if vice_leader and user.id == vice_leader.get('id') else "member")
        }
        for user in users
    ]
    
    response_data = {
        "success": True, 
        "message": "This is the information about the team you need", 
        "data": team, 
        "leader": leader, 
        "viceLeader": vice_leader, 
        "members": users 
    }
    
    return response_data 
      
# [POST] 

                
def update_team(userID , id , data): #id = teamID 
    data = dict(data) 
    
    icon = data.get('icon')  
    banner = data.get('banner') 
    name = data.get('teamName') 
    description = data.get('teamDescription')
    leaderID = data.get('leaderID')
    viceLeaderID = data.get('viceLeaderID')
    response_data = {
        "teamID": id 
    }
    team = db.session.query(Team).filter(Team.id == id).first() 
    # Update team name 
    if name is not None: 
        team.name = name 
    # Update icon 
    if icon is not None: 
        iconUrl = uploadTeamImage(team , icon , 'icon') 
        response_data["iconUrl"] = iconUrl 
    # Update banner 
    if banner is not None: 
        bannerUrl = uploadTeamImage(team , banner , 'banner') 
        response_data["bannerUrl"] = bannerUrl 
    # Update description 
    if description is not None: 
        team.description = description 
        response_data["description"] = description
    # Update Leader ID 
    currentLeader = team.leader_id 
    if leaderID is not None:
        if currentLeader == userID:
            Leader = db.session(User).filter(leaderID == User.id).first() 
            if Leader: 
                team.leader = Leader 
                team.leader_id = leaderID 
            else: 
                response_data["viceLeaderID"] = "Error in find leader"
        else: 
            response_data['leaderID'] = "You dont't have permission to do this" 
    # Update vice leader 
    if viceLeaderID is not None:
        if currentLeader == userID: 
            ViceLeader = db.session(User).filter(viceLeaderID == User.id).first() 
            if ViceLeader: 
                team.vice_leader = ViceLeader 
                team.vice_leader_id = viceLeaderID 
            else: 
                response_data["viceLeaderID"] = "Error in find vice leader"
        else: 
            response_data['viceLeaderID'] = "You dont't have permission to do this"
    #Update database 
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
    
    db.session.execute(
        assignment_association.delete().where(assignment_association.c.task_id.in_([t.id for t in tasks]))
    )

    db.session.execute(
        team_member_association.delete().where(team_member_association.c.team_id == id)
    )
    
    for x in tasks: 
        db.session.delete(x) 
    inviteCode = db.session.query(InviteCode).filter(InviteCode.team_id == id).first() 
    db.session.delete(inviteCode) 
    db.session.delete(team) 
    db.session.commit() 
    return {
        "success": True, 
        "message": "Your team has been deleted successfully"
    }

    
def join_code(code , userID): 
    qr = db.session.query(InviteCode).filter(InviteCode.code == code).first() 
    if qr: 
        team_id = qr.team_id 
        team = db.session.query(Team).filter(Team.id == team_id).first() 
        user = db.session.query(User).filter(User.id == userID).first() 
        if team and user: 
            exists_stmt = select(team_member_association).where(
                team_member_association.c.user_id == user.id,
                team_member_association.c.team_id == team_id
            )

            row = db.session.execute(exists_stmt).first()

            if row:
                return {
                    "success": False,
                    "message": "User already joined this team"
            }
            stmt = team_member_association.insert().values(
                team_id = team_id, 
                user_id = user.id 
            )
            db.session.execute(stmt) 
            db.session.commit() 
            response_data = {
                "success": True, 
                "message": "Join team successfully", 
                "data": {
                    "teamID": team_id, 
                    "joinAt": toStr(getNow()), 
                    "teamName": team.name 
                }
            }
            return response_data 
        else: return {
            "success": False, 
            "message": "Cannot find the team with this code"
        }
    return {
        "success": False, 
        "message": "The code is invalid"
    }