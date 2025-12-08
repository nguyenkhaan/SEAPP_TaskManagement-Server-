import os 
from redis import Redis

# Giả sử bạn đã set REDIS_URL trong environment:
# REDIS_URL = "redis://:mypassword@redis-production-363b.up.railway.app:6379/0"

app_cache = Redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
jwt_blacklist = Redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
