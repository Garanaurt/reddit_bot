import redis
from rq import Queue, Worker, Connection
import multiprocessing



num_workers = 3



redis_conn = redis.Redis(host='localhost', port=6379)
queue = Queue(connection=redis_conn)

def worker_process():
    with Connection(redis_conn):
        worker = Worker([queue])
        worker.work(with_scheduler=True)


def main():
    try:
        redis_conn.ping()
        print("Redis server - ok")
    except redis.ConnectionError:
        print("No connection to Redis.")
        return

    worker_processes = []

    for _ in range(num_workers):
        worker_process_instance = multiprocessing.Process(target=worker_process)
        worker_process_instance.daemon = False
        worker_process_instance.start()
        worker_processes.append(worker_process_instance)

    lock = multiprocessing.Lock()
    while True:
        with lock:
            lock.acquire()


if __name__ == "__main__":
    main()


