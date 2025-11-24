from ..models import db
from ..models.association import team_member_association
from ..models.team_model import Team
from sqlalchemy import select, exists

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