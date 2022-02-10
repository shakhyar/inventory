import sqlite3
import datetime

conn = sqlite3.connect("dashboard.db", check_same_thread=False)
c = conn.cursor()


class Inventory:
    """
    #? Table name = assets
    #* Columns: product id, name, price

    """
    def __init__(self):
        self.create_table(True)
        self.create_history(True)
        self.crete_long_history(True)
        self.row = []


    def create_table(self, true):
        self.true = true
        if self.true:
            c.execute("CREATE TABLE IF NOT EXISTS dashboard(product_id TEXT, name TEXT, price INT, quantity INT)")
            conn.commit()
        else:
            pass


    def product_entry(self, pid, name, price, quantity):
        self.id = pid
        self.name = name
        self.quantity = quantity
        self.price = price
        
        c.execute("SELECT * FROM dashboard")
        c.execute("INSERT INTO dashboard(product_id, name, price, quantity) VALUES (?, ?, ?, ?)", (self.id, self.name, self.price, self.quantity))
        conn.commit()


    def get_dashboard(self):
        self.row = []
        c.execute("SELECT * FROM dashboard")
        for row in list(c.fetchall()):
            self.row.append(row)

        return self.row

    def get_dash_name(self, pid):
        c.execute("SELECT * FROM dashboard WHERE product_id = ?", (pid,))
        for row in list(c.fetchall()):
            return row[1]


    def update_quantity(self, pid, quantity):
        # if user click on the edit button side of it, it sends to edit quantity page
        # change the inventory value if pid entered
        c.execute("UPDATE dashboard set quantity = ? where product_id = ?", (quantity, pid,))
        conn.commit()


    def update_inventory_price(self, pid, price):
        c.execute("UPDATE dashboard set price = ? where product_id = ?", (price, pid,))
        conn.commit()


    def inventory_price(self):
        c.execute(f"SELECT * FROM dashboard")
        self.price = 0
        for row in list(c.fetchall()):
            self.price = self.price+row[2]

        return self.price

    def del_product(self, pid):
        c.execute("DELETE FROM dashboard WHERE product_id= ?", (pid,))
        conn.commit()


    def create_history(self, true):
        self.true = true
        if self.true:
            c.execute("CREATE TABLE IF NOT EXISTS history(product_id TEXT, name TEXT, price INT, profit REAL, now TIMESTAMP)")
            conn.commit()
        else:
            pass 

    
    def history_input(self, pid, name, profit, price):
        self.id = pid
        self.name = name
        self.price = int(price)
        self.profit = profit
        self.time = datetime.datetime.now()
        self.time = self.time.strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute("SELECT * FROM history")
        c.execute("INSERT INTO history(product_id, name, price, profit, now) VALUES (?, ?, ?, ?, ?)", (self.id, self.name, self.price, self.profit, self.time))
        conn.commit()


    def get_history(self):
        self.history = []
        c.execute("SELECT * FROM history")
        for row in list(c.fetchall()):
            self.history.append(row)

        return self.history


    def calculate_revenue(self):
        """
        return: [price, profit]
        """
        c.execute(f"SELECT * FROM history")
        self.price = 0
        self.profit = 0
        for row in list(c.fetchall()):
            self.price = self.price + row[2]
            self.profit = self.profit + row[3]
        return [self.price, self.profit]

    def del_history_product(self, pid):
        c.execute("DELETE FROM history WHERE product_id= ?", (pid,))
        conn.commit()


    def end_session(self):
        self.revenue = self.calculate_revenue()
        self.long_history_input(self.revenue)
        c.execute("DELETE FROM history;")
        conn.commit()


    def crete_long_history(self, true):
        self.true = true
        if self.true:
            c.execute("CREATE TABLE IF NOT EXISTS long_history(month TEXT, price INT, profit REAL, now TIMESTAMP)")
            conn.commit()
        else:
            pass 


    def long_history_input(self, revenue_list):
        mydate = datetime.datetime.now()
        self.month = mydate.strftime("%B") + str(datetime.date.today().year)
        self.price = int(revenue_list[0])
        self.profit = int(revenue_list[1])
        self.time = mydate.strftime('%d-%m %H:%M:%S')
        
        c.execute("SELECT * FROM long_history")
        c.execute("INSERT INTO long_history(month, price, profit, now) VALUES (?, ?, ?, ?)", (self.month, self.price, self.profit, self.time))
        conn.commit()


    def get_long_history(self):
        self.row = []
        c.execute("SELECT * FROM long_history")
        for row in list(c.fetchall()):
            self.row.append(row)

        return self.row        


    def long_history_sum(self):
        """
        return: [totalprice, totalprofit]
        """
        c.execute("SELECT * FROM long_history")
        self.price = 0
        self.profit = 0
        for row in list(c.fetchall()):
            self.price = self.price + row[1]
            self.profit = self.profit + row[2]

        return [self.price, self.profit]


    def del_long_history(self, now):
        c.execute("DELETE FROM long_history WHERE now= ?", (now,))
        conn.commit()


    def last_pid_dashboard(self):
        c.execute("SELECT * FROM dashboard ORDER BY product_id DESC LIMIT 1",)
        pid = c.fetchone()
        return pid

    def last_pid_history(self):
        c.execute("SELECT * FROM history ORDER BY product_id DESC LIMIT 1",)
        pid = c.fetchone()
        return pid[0]

    # TODO: - add employee, salary, profit=profit-salary
    # - add profit input window = enter profit ammount on a particular product
    # - add profit column to the history table, to later use if for vizualization purposes.