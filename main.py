from datetime import timedelta

from flask import Flask, render_template, request, url_for, redirect, session
from babel.numbers import format_currency

from accounts import Users
from dash import Inventory

app = Flask(__name__)
app.secret_key = "........"
app.permanent_session_lifetime = timedelta(minutes=30)
ac_db = Users()
inventory = Inventory() 


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["email"]
        password = request.form["password"]
        print(user, password)
        active, msg = ac_db.validate(user, password)
        if active:
            session["user"] = user
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", msg=msg)
    else:
        if "user" in session:
            return redirect(url_for("dashboard"))

        return render_template("login.html")


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
	if 'user' in session:
		if request.method == "POST":
			action = request.form['btn']
			flag = action[:action.index(':')]

			if flag == "edit":
				pid = int(action[action.index(':')+1:action.index('+')])
				price = int(action[action.index('+')+1:action.index('/')])
				quantity = int(action[(action.index('/')+1):])
				pp = price/quantity
				print(pp)
				return redirect(url_for('edit_inventory', pid=pid, pr=pp))
			
			elif flag == "sold":
				# extracts the information of the given pid, redirects to profit page, and returns to dashboard
				pid = int(action[action.index(':')+1:action.index('+')])
				price = int(action[action.index('+')+1:action.index('/')])
				quantity = int(action[(action.index('/')+1):])
				pp = price/quantity
				return redirect(url_for('sold', pid=pid, quantity=quantity, pr=pp, orp=price, orq=quantity))
			
			else:
				pid = int(action[action.index(':')+1:])
				inventory.del_product(pid)
				return redirect(url_for('dashboard'))

		else:
			user = session['user']
			items = inventory.get_dashboard()
			worth = inventory.inventory_price()
			items.sort(reverse=True)
			return render_template('dashboard.html', items = items, worth=format_currency(worth, 'INR', locale='en_IN'))
	else:
		return redirect(url_for('login'))


@app.route('/add-inventory', methods=["GET", "POST"])
def add_inventory():
	if 'user' in session:
		if request.method == 'POST':
			pid = inventory.last_pid_dashboard()
			if not pid:
				pid = 1
			else:
				pid = int(pid[0]) + 1
			name = request.form['name']
			price = int(request.form['price'])
			quantity = int(request.form['quantity'])
			print(price, quantity, price*quantity)

			inventory.product_entry(pid, name, price*quantity, quantity)
			return redirect(url_for('dashboard'))
		else:
			return render_template('add_invent.html')
	else:		
		return redirect(url_for('login'))


@app.route('/edit_inventory/<pid>/<pr>', methods=["GET", "POST"])
def edit_inventory(pid, pr):
	if 'user' in session:
		if request.method == 'POST':
			new_quantity = request.form['quantity']
			np = int(float(pr))*int(new_quantity)
			print("======  new price", np)
			inventory.update_quantity(pid, new_quantity)
			inventory.update_inventory_price(pid, np)
			return redirect(url_for('dashboard'))
		else:
			return render_template('edit_inventory.html')
	else:
		return render_template('edit_inventory.html')


@app.route('/sold/<pid>/<quantity>/<pr>/<orp>/<orq>', methods=["GET", "POST"])
def sold(pid, quantity, pr, orp, orq):
	pid = int(pid)
	quantity = int(quantity)
	pr = int(float(pr))
	orp = int(orp)
	orq = int(orq)
	"""/passed params will be pid, quantity and pr.
	   /quantity is the total quantity in inventory

	   /take the number of items to sold, multiply it with pr
	   /and then subtract from orp, store it in new_price

	   /also new quantity = originalquantity-newquantity

	   /###TAKE CARE OF PROFIT FIELD - MULTIPLy PROFIT INPUT WITH QTY#

	   /update opr and new quantity from the update functinos. We have
	   to add another update function for updating price

	   store the new values along with the name(have to create another function to
	   get the name) along with new prices, old pid, and profit in the new dashboard,
	   redirect to monthly

	"""
	if 'user' in session:
		if request.method == 'POST':

			sold_qty = int(request.form['sold_qty'])
			profit = int(request.form['profit'])

			total_sp = pr*sold_qty
			new_price = orp - total_sp

			total_profit = profit*sold_qty

			new_quantity = orq - sold_qty
			name = str(inventory.get_dash_name(pid))

			inventory.history_input(pid, name, total_profit, total_sp)
			inventory.update_inventory_price(pid, new_price)
			inventory.update_quantity(pid, new_quantity)

			return redirect(url_for('dashboard'))
		else:
			return render_template('sell.html')
	else:
		return render_template('login.html')	


@app.route('/monthly', methods=['GET', 'POST'])
def monthly():
	if 'user' in session:
		if request.method == 'POST':
			action = request.form['btn']
			flag = action[:action.index(':')]

			if flag == 'delete':
				pid = int(action[action.index(':')+1:])
				inventory.del_history_product(pid)
				return redirect(url_for('monthly'))
		else:
			history=[]
			history = inventory.get_history()
			worth = inventory.calculate_revenue()
			history.sort(reverse=True)
			return render_template('monthly.html', history=history, worth=worth)
	else:
		return redirect(url_for('login'))


@app.route('/yearly-commit')
def yerly_commit():
	if 'user' in session:
		inventory.end_session()
		return redirect(url_for('yearly'))
	else:
		return redirect(url_for('login'))


@app.route('/yearly', methods=['GET', 'POST'])
def yearly():
	if 'user' in session:
		if request.method == 'POST':
			action = request.form['btn']
			flag = action[:action.index(':')]

			if flag == 'delete':
				now = action[action.index(':')+1:]
				inventory.del_long_history(now)
				return redirect(url_for('yearly'))
		else:
			yearly=[]
			yearly = inventory.get_long_history()
			worth = inventory.long_history_sum()
			yearly.sort(reverse=True)
			return render_template('yearly.html', history=yearly, worth=worth)
	else:
		return redirect(url_for('login'))


@app.route('/logout')
def logout():
	if 'user' in session:
		session.pop('user', None)
		return redirect(url_for('login'))
	else:
		return "Already logged out"

print("""
⠄⠄⣿⣿⣿⣿⠘⡿⢛⣿⣿⣿⣿⣿⣧⢻⣿⣿⠃⠸⣿⣿⣿⠄⠄⠄⠄⠄
⠄⠄⣿⣿⣿⣿⢀⠼⣛⣛⣭⢭⣟⣛⣛⣛⠿⠿⢆⡠⢿⣿⣿⠄⠄⠄⠄⠄
⠄⠄⠸⣿⣿⢣⢶⣟⣿⣖⣿⣷⣻⣮⡿⣽⣿⣻⣖⣶⣤⣭⡉⠄⠄⠄⠄⠄
⠄⠄⠄⢹⠣⣛⣣⣭⣭⣭⣁⡛⠻⢽⣿⣿⣿⣿⢻⣿⣿⣿⣽⡧⡄⠄⠄⠄
⠄⠄⠄⠄⣼⣿⣿⣿⣿⣿⣿⣿⣿⣶⣌⡛⢿⣽⢘⣿⣷⣿⡻⠏⣛⣀⠄⠄
⠄⠄⠄⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠙⡅⣿⠚⣡⣴⣿⣿⣿⡆⠄
⠄⠄⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠄⣱⣾⣿⣿⣿⣿⣿⣿⠄
⠄⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⠄
⠄⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠣⣿⣿⣿⣿⣿⣿⣿⣿⣿⠄
⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠑⣿⣮⣝⣛⠿⠿⣿⣿⣿⣿⠄
⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⠄⠄⠄⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠄
""")
if __name__ == '__main__':
	app.run(debug=True)