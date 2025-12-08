from redis import Redis
from dotenv import load_dotenv
import os

load_dotenv()

app_cache = Redis(host=os.environ.get('REDISHOST'), port=6379, password=os.getenv('REDISPASSWORD'), decode_responses=True, db=0)

jwt_blacklist = Redis(host=os.environ.get('REDISHOST'), port=6379, password=os.getenv('REDISPASSWORD'), decode_responses=True, db=0) 


