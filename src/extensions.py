import os 
from redis import Redis

app_cache = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
jwt_blacklist = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

