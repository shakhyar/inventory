import sqlite3

uconn = sqlite3.connect("users.db", check_same_thread=False)
uc = uconn.cursor()


class Users:
    """
    #? Table name = user
    #* Columns: username, password

    """
    def __init__(self):
        self.create_table(True)
        self.column1 = []

    def create_table(self, true):
        self.true = true
        if self.true:
            uc.execute("CREATE TABLE IF NOT EXISTS user(username TEXT, password TEXT)")
            uconn.commit()
            self.user_entry('admin', 'admin123')
        else:
            pass

    def user_entry(self, username, password):
        self.username = username
        self.password = password
        
        uc.execute("SELECT * FROM user")
        uc.execute("INSERT INTO user(username, password) VALUES (?, ?)", (self.username, self.password))
        uconn.commit()

    def validate(self, username, password):
        self.username = str(username)
        self.password = str(password)
        uc.execute(f"SELECT * FROM user")
        for row in list(uc.fetchall()):
            if self.username == row[0]:
                if self.password == row[1]:
                    return True, ""
                else:
                    return False, "Invalid credentials or user not recognized"
