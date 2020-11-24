import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.TABLE_NAME = 'timers'
        self.cursor.execute('''Create TABLE if not exists timers(
                    timer_owner TEXT,
                    timer_name TEXT, 
                    interval_time TEXT, 
                    interval_miss_limit INTEGER, 
                    recipient_list TEXT, 
                    message TEXT,
                    status INTEGER,
                    PRIMARY KEY (timer_owner, timer_name) 
                )
            ''')

    async def insert(self, author, timer_name, interval_time, interval_miss_limit, recipient_list, message, status):
        try:
            self.cursor.execute(
                "INSERT INTO timers VALUES(?, ?, ?, ?, ?, ?, ?)",
                (author, timer_name, interval_time, interval_miss_limit, recipient_list, message, status)
            )

            self.conn.commit()

        except sqlite3.Error as e:

            if 'UNIQUE constraint failed' in e:
                return "UNIQUE-FAIL"
            return "INSERT-FAIL"

        return 'SUCCESS'


