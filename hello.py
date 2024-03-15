from flask import Flask, render_template


# create a flask app
app = Flask(__name__)


@app.route('/')
def index():
    first_name = "Mcodex"
    return render_template('index.html', first_name=first_name)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# internal server error
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 505



if __name__ == '__main__':
    app.run(debug=True)