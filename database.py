# database.py

import sqlite3
from datetime import date


class Database:
    def __init__(self):
        self.con = sqlite3.connect('mydatabase.db')
        self.cursor = self.con.cursor()

        # create the user and task table if they don't already exist
        self.create_user_table()
        self.create_task_table()

    def create_user_table(self):
        """Create the user table"""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users(id integer PRIMARY KEY AUTOINCREMENT, email varchar(50) NOT NULL, user_password varchar(50) NOT NULL, loggedin BOOLEAN NOT NULL CHECK (loggedin IN (0, 1)), keeploggedin BOOLEAN NOT NULL CHECK (keeploggedin IN (0, 1)))")
        self.con.commit()

    def create_user(self, email, password, keeploggedin=0):
        """Create a user"""
        self.cursor.execute("INSERT INTO users(email, user_password, loggedin, keeploggedin) VALUES(?, ?, ?, ?)", (email, password, 0, keeploggedin))
        self.con.commit()

    def check_username(self, email):
        """Check to see if the email already exists in the database before going onto creating a user"""
        the_user = self.cursor.execute("SELECT id, email FROM users WHERE email = ?", (email,)).fetchall()
        if the_user == []:
            return False
        else:
            return True

    def get_user(self, email, password, keepmelogged):
        """Get the user when loggin in to the system"""
        user_id = self.cursor.execute("SELECT id FROM users WHERE email=? AND user_password=?", (email, password)).fetchall()
        if user_id:
            self.cursor.execute("UPDATE users SET loggedin = 0 WHERE loggedin = 1")
            if keepmelogged == True:
                self.cursor.execute("UPDATE users SET loggedin = 1, keeploggedin = 1 WHERE id = ?", (user_id[0]))
            else:
                self.cursor.execute("UPDATE users SET loggedin = 1 WHERE id = ?", (user_id[0]))


            self.con.commit()
            return True
        else:
            return False

    
    def get_logged_in_user_email(self):
        """Get the currently logged in user"""
        email = self.cursor.execute("SELECT email FROM users WHERE loggedin = 1").fetchall()
        return email[0][0]


    def get_logged_in_userid(self):
        """Get the userid of the currently logged in user"""
        userid = self.cursor.execute("SELECT id FROM users WHERE loggedin = 1").fetchall()
        return userid[0]

    def get_keep_logged_in(self):
        '''Check if there is any user with keepmelogged = 1'''
        logged = self.cursor.execute("SELECT * FROM users WHERE keeploggedin = 1").fetchall()
        if logged == []:
            return False
        else:
            return True





    def log_out_user(self):
        """Triggered when the user logsout"""
        self.cursor.execute("UPDATE users SET loggedin = 0, keeploggedin = 0 WHERE loggedin = 1")
        self.con.commit()

    

    


    #----------------------------------------------------------CREATE TASKS------------------------------------------------------------#

    def create_task_table(self):
        """Create tasks table"""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks(id integer PRIMARY KEY AUTOINCREMENT, userid integer NOT NULL, task varchar(50) NOT NULL, date_completed DATE, completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)), FOREIGN KEY (userid) REFERENCES users (id))")
        self.con.commit()
        

    def create_task(self, userid, task, date_completed=None):
        """Create a task"""
        self.cursor.execute("INSERT INTO tasks(userid, task, date_completed, completed) VALUES(?, ?, ?, ?)", (userid, task, date_completed, 0))
        self.con.commit()

        # GETTING THE LAST ENTERED ITEM SO WE CAN ADD IT TO THE TASK LIST
        created_task = self.cursor.execute("SELECT id, task FROM tasks WHERE userid = ? and task = ? and completed = 0", (userid, task)).fetchall()

        return created_task[-1]

    def get_tasks(self, userid):
        """Get tasks when loggin into the system"""
        uncomplete_tasks = self.cursor.execute("SELECT id, task, completed FROM tasks WHERE userid=? and completed = 0", (userid,)).fetchall()
        completed_tasks = self.cursor.execute("SELECT id, task, completed FROM tasks WHERE userid=? and completed = 1", (userid,)).fetchall()

        return completed_tasks, uncomplete_tasks

    def mark_task_as_complete(self, userid, taskid):
        """Marking tasks as complete"""
        date_completed = date.today()
        self.cursor.execute("UPDATE tasks SET completed=1, date_completed=? WHERE userid=? AND id=?", (date_completed,userid, taskid))
        self.con.commit()

    def mark_task_as_uncomplete(self, userid, taskid):
        """Mark task as uncomplete"""
        self.cursor.execute("UPDATE tasks SET completed=0, date_completed=? WHERE userid=? AND id=?", (None, userid, taskid))
        self.con.commit()

    def delete_task(self, userid, taskid):
        """Delete a task"""
        self.cursor.execute("DELETE FROM tasks WHERE userid=? AND id=?", (userid, taskid))
        self.con.commit()

    def close_db_connection(self):
        self.con.close()