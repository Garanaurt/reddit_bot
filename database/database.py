import sqlite3
import os

db_path = "data.db"

class DbShop:
    def __init__(self) -> None:
        self.db_path = None

    def db_initialize(self):
        print('Database was started')
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def db_close_conn(self):
        print('Database was closed')
        self.conn.close()



    def set_done_to_param(self, url):
        self.cursor.execute("UPDATE params SET done = TRUE WHERE url = ?", (url,))
        self.conn.commit()
        print(f'Vote for {url} was done')





    def db_add_param_from_usr(self, params):
        count = int(params[0])
        sleep_time = int(params[1])
        url = params[2]
        self.cursor.execute("INSERT INTO params (url, vote_cnt, sleep_time) VALUES (?, ?, ?)", (url, count, sleep_time))
        self.conn.commit()




    def db_save_job_result(self, job_id, result):
        self.cursor.execute("UPDATE jobs SET result = ? WHERE job_id = ?", (result, job_id))
        self.conn.commit()
        print(f'job {job_id} has result {result}')



    def db_add_job(self, job_id, url, vote_cnt, sleep_time):
        self.cursor.execute("INSERT INTO jobs (job_id, url, vote_cnt, sleep_time) VALUES (?, ?, ?, ?)", (job_id, url, vote_cnt, sleep_time))
        self.conn.commit()
        print(f'{job_id} was added')



    
    def db_get_all_params(self):
        self.cursor.execute("SELECT * FROM params")
        result = self.cursor.fetchall()
        return result
    


    def get_jobs_where_url(self, url):
        self.cursor.execute("SELECT * FROM jobs WHERE url = ?", (url,))
        result = self.cursor.fetchall()
        return result



    def get_count_job_where_ok(self, url):
        self.cursor.execute("SELECT COUNT(*) FROM jobs WHERE result = 'upvote_ok' AND url = ?",(url, ))
        count = self.cursor.fetchone()[0]
        print('job ok', count)
        return count




    def db_check_and_create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs(
            job_id text,
            url text,
            vote_cnt INTEGER,
            sleep_time INTEGER,
            result text DEFAULT "not_start",
            adding_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (job_id)
            )''')
        self.conn.commit()
        print("table jobs was created")


        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS params(
            url text,
            vote_cnt INTEGER,
            sleep_time INTEGER,
            adding_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            done BOOLEAN DEFAULT FALSE
            )''')
        self.conn.commit()
        print("table params was created")
