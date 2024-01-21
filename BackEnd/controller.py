from flask import Flask, jsonify, render_template, request, redirect, url_for
import pymongo
from dal import UserAccountDAO
'''from services import getSystemInfo'''
app = Flask(__name__)



# This route displays the 'authentification.html' template
@app.route('/')
def show_authentification():
    return render_template('authentification.html')

# The actual authentication logic can be handled in a different route, let's call it 'authenticate'
from flask import redirect

@app.route('/authenticate', methods=['POST'])
def authenticate():
    user_dao = UserAccountDAO()

    # Get form data
    username = request.form.get('username')
    password = request.form.get('password')
    action = request.form.get('action')

    # Your authentication logic here
    if action == 'login':
        result = user_dao.verify_user_credentials(username, password)
        if result:
            # Successful login
            return redirect(url_for('dashboard'))
        else:
            # Invalid username or password
            return render_template('authentification.html', error='Invalid username or password')

    elif action == 'signup':
        # Redirect to signup page
        return redirect(url_for('signup'))

    # Handle other cases if needed

    return render_template('authentification.html')



# The dashboard and signup routes remain the same
@app.route('/dashboard')
def dashboard():
    # Add authentication check here if needed
    return "Welcome to the Dashboard!"
@app.route('/signUp')
def signUp():
    return render_template('signUp.html')


@app.route('/signup', methods=['POST'])
def signup():
        user_dao = UserAccountDAO()

   
        # Handle signup form submission
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username is already taken
        if user_dao.get_user_by_username(username):
            return render_template('signUp.html', error='Username already exists. Choose a different one.')

        # Create a new user account
        user=user_dao.create_user(username, password)

        if user :
            return "True"
        else :
            return "False"

    # Render the signup form for GET requests
'''
@app.route('/snmp-info', methods=['GET'])
def snmp_info():
    system_info = getSystemInfo('127.0.0.1')
    result = {
        'memory_size': system_info[0],
        'memory_used': system_info[1],
        'cpu_load': system_info[2]
    }
    return jsonify(result)
   
'''
if __name__ == '__main__':
    app.run(debug=True)