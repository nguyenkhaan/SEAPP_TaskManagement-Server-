import os 
from redis import Redis

app_cache = Redis(
    host="127.0.0.1",
    port=6379,
    password=os.environ.get('REDISPASSWORD'),
    decode_responses=True,
    db=0
)
jwt_blacklist = Redis(
    host="127.0.0.1",
    port=6379,
    password=os.environ.get('REDISPASSWORD'),
    decode_responses=True,
    db=0
)
