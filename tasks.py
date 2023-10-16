from celery import shared_task
from celery.utils.log import get_task_logger
from create_db import db
from redis import Redis
from rq import Queue
from rq.registry import ScheduledJobRegistry
from datetime import timedelta
import asyncio
import random
from worker import gomain


def get_users():
    users_data = []
    with open('users.txt', 'r') as f:
        acc_list = f.readlines()
        for line in acc_list:
            user_data = line.split(':')
            users_data.append(user_data)
    return users_data

logger = get_task_logger(__name__)

@shared_task
async def add_to_queu_task(params):
    print('go')
    try:
        redis_conn = Redis(host='localhost', port=6379)
        logger.info("Redis server - ok")
        print(f"ok")
    except (OSError, ConnectionError) as e:
        logger.error(f"Could not connect to Redis: {e}")
        print(f"Could not connect to Redis: {e}")
        return

    log_pass = get_users()
    count = int(params[0])
    sleep_time = int(params[1])
    url = params[2]

    queue = Queue(connection=redis_conn)

    if count > len(log_pass):
        cnt = len(log_pass)
    else:
        cnt = count

    indices = list(range(len(log_pass)))
    random.shuffle(indices)

    #count_up = db.get_count_job_where_err()
    while db.get_count_job_where_ok(url) <= cnt:
        try:
            rand = indices.pop()
        except Exception:
            print('Закончились аакаунты')
            db.set_done_to_param(url)
            return
        user = log_pass[rand]
        login = user[0]
        password = user[1]
        arg = (login, password, url)
        job = queue.enqueue_in(timedelta(seconds=2), gomain, arg)
        #print('job in q')
        job_id = job.get_id()
        print(job_id)
        registry = ScheduledJobRegistry(queue=queue)
        #count_up += 1
        db.db_add_job(job_id, url, cnt, sleep_time)
        #logger.info(job in registry)
        
        await asyncio.sleep(sleep_time)
    else:
        db.set_done_to_param(url)


    redis_conn.close()



