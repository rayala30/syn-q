import redis
import os

# Get the Redis URL from environment variables (configured in Railway)
REDIS_URL = os.getenv('REDIS_URL')

# Connect to Redis
redis_client = redis.Redis.from_url(REDIS_URL)

# Optionally, you can test the connection
try:
    redis_client.ping()
    print("Successfully connected to Redis!")
except redis.ConnectionError:
    print("Failed to connect to Redis.")
