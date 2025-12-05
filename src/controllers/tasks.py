from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .parsers import update_task_parser, search_tasks_parser, create_task_parser


from ..services.tasks_service import (
    getTaskStatistics,  # Da noi 
    getTaskStatisticsByTeamId, # Da noi 
    getTasksOverview,
    getAllUserTasksGroupedByTeam,
    getTaskDetail,
    updateTaskById,
    deleteTaskById,
    searchTasks,
    createTask, # Da noi 
    getTeamTasks
)

tasks_bp = Blueprint('tasks', __name__)
tasks_api = Api(tasks_bp)



class TaskStatistics(Resource):

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        result = getTaskStatistics(user_id=user_id)
        return result


class TaskStatisticsByTeam(Resource):

    @jwt_required()
    def get(self, teamId):
        user_id = int(get_jwt_identity())
        result = getTaskStatisticsByTeamId(user_id=user_id, team_id=teamId)
        return result


class TasksOverview(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        result = getTasksOverview(user_id=user_id)
        return result


class AllUserTasks(Resource):

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        result = getAllUserTasksGroupedByTeam(user_id=user_id)
        return result

class TaskDetail(Resource):
    @jwt_required()
    def get(self, taskId):
        user_id = int(get_jwt_identity())
        result = getTaskDetail(user_id=user_id, task_id=taskId)
        return result

    @jwt_required()
    def put(self, taskId):
        user_id = int(get_jwt_identity())
        args = update_task_parser.parse_args()

        # Lọc các trường có giá trị None
        update_data = {k: v for k, v in args.items() if v is not None}

        result = updateTaskById(user_id=user_id, task_id=taskId, data=update_data)

        return result

    @jwt_required()
    def delete(self, taskId):
        user_id = int(get_jwt_identity())
        result = deleteTaskById(user_id=user_id, task_id=taskId)
        return result

class TaskSearch(Resource):

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        args = search_tasks_parser.parse_args()

        query = args.get('q')
        team_id = args.get('teamId')
        status = args.get('status')
        important = args.get('important')

        result = searchTasks(
            user_id=user_id,
            query=query,
            team_id=team_id,
            status=status,
            important=important
        )
        return result


class TeamTasksResource(Resource):

    @jwt_required()
    def post(self, teamId):
        user_id = int(get_jwt_identity())
        args = create_task_parser.parse_args()
        data = {k: v for k, v in args.items() if v is not None}
        result = createTask(user_id=user_id, team_id=teamId, data=data)
        return result

    @jwt_required()
    def get(self, teamId):
        user_id = int(get_jwt_identity())
        result = getTeamTasks(user_id=user_id, team_id=teamId)
        return result


tasks_api.add_resource(TaskStatistics, '/statistics')
tasks_api.add_resource(TaskStatisticsByTeam, '/statistics/teams/<string:teamId>')
tasks_api.add_resource(TasksOverview, '/overview')
tasks_api.add_resource(AllUserTasks, '/me')
tasks_api.add_resource(TaskDetail, '/<string:taskId>')
tasks_api.add_resource(TaskSearch, '/search')
tasks_api.add_resource(TeamTasksResource, '/teams/<string:teamId>/tasks')