from redis import Redis
from dotenv import load_dotenv
import os

load_dotenv()

app_cache = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
jwt_blacklist = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)


