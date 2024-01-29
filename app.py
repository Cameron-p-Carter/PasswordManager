from flask import Flask, render_template, request, redirect, url_for, session
import json


class User():
    def __init__(self, user_name, user_password):
        self._user_name = user_name
        self._user_password = user_password
        self._sites = []
   
    def getUserName(self):
        return self._user_name
   
    def getUserPassword(self):
        return self._user_password
   
    def addSite(self, x):
        self._sites.append(x)

    def getSites(self):
        return self._sites

    def getSite(self, x):
        return self._site[x]


class Site():
    def __init__(self, site_name, site_user_name, site_password):
        self._site_name = site_name
        self._site_user_name = site_user_name
        self._site_password = site_password

    def getSiteName(self):
        return self._site_name
   
    def getSiteUsername(self):
        return self._site_user_name
   
    def getSitePassword(self):
        return self._site_password


   
   
class Manager:
    def __init__(self):
        self._all_users = []

    def createUser(self, user_name, user_password):
        new_user = User(user_name, user_password)
        self._all_users.append(new_user)

    def findUserByUsername(self, user_name):
        for user in self._all_users:
            if user.getUserName() == user_name:
                return user
        return None
   
    def authenticateUser(self, user_name, user_password):
        for user in self._all_users:
            if user.getUserName() == user_name and user.getUserPassword() == user_password:
                return user
        return None
   
    def addSiteForUser(self, user, site_name, site_user_name, site_password):
        new_site = Site(site_name, site_user_name, site_password)
        user.addSite(new_site)

    def loadDataFromJsonFile(self):
        try:
            with open('password_data.json', 'r') as file:
                data = json.load(file)
                for user_data in data.get('users', []):
                    user = User(user_data['username'], user_data['password'])
                    for site_data in user_data.get('sites', []):
                        site = Site(site_data['site_name'], site_data['username'], site_data['password'])
                        user.addSite(site)
                    self._all_users.append(user)
        except FileNotFoundError:
            pass

    def saveDataToJsonFile(self):
        data = {"users": []}
        for user in self._all_users:
            user_data = {"username": user.getUserName(), "password": user.getUserPassword(), "sites": []}
            for site in user.getSites():
                site_data = {"site_name": site.getSiteName(), "username": site.getSiteUsername(), "password": site.getSitePassword()}
                user_data["sites"].append(site_data)
            data["users"].append(user_data)

        with open('password_data.json', 'w') as file:
            json.dump(data, file)






app = Flask(__name__)
manager = Manager()
manager.loadDataFromJsonFile()



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = manager.authenticateUser(username, password)

    if user:
        session['user'] = {
            'user_name': user.getUserName(),
            'user_password': user.getUserPassword(),
            'sites': [{'site_name': site.getSiteName(), 'username': site.getSiteUsername(), 'password': site.getSitePassword()} for site in user.getSites()]
        }
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html', error_message="Incorrect username or password")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        manager.createUser(username, password)
        manager.saveDataToJsonFile()
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user_data = session.get('user')
    if not user_data:
        return redirect(url_for('index'))

    user = User(user_data['user_name'], user_data['user_password'])
    for site_data in user_data['sites']:
        site = Site(site_data['site_name'], site_data['username'], site_data['password'])
        user.addSite(site)

    if request.method == 'POST':
        site_name = request.form['site_name']
        site_user_name = request.form['site_user_name']
        site_password = request.form['site_password']

        user.addSite(Site(site_name, site_user_name, site_password))

        existing_user = manager.findUserByUsername(user.getUserName())
        existing_user.getSites().append(Site(site_name, site_user_name, site_password))

        manager.saveDataToJsonFile()

    return render_template('dashboard.html', user=user)


app.secret_key = 'key'

if __name__ == '__main__':
    app.run(debug=True)

