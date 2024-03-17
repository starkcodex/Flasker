from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


# create a flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/users_db'
app.config['SECRET_KEY'] = 'xtransparent zozilla'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Name %r>' % self.name
    
    
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    favourite_color = StringField('Favourite Color')
    submit = SubmitField("Submit")


# create a form for input 
class NamerForm(FlaskForm):
    name = StringField('Please Enter Your Name:', validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    
    
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        try:
            db.session.commit()
            flash('User updated Successfully.')
            return render_template('update.html', 
                                    form=form, 
                                    name_to_update = name_to_update)
        except:
            flash('Error. something went wrong')
            return render_template('update.html', form=form, name_to_update=name_to_update )
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update)

    
    
@app.route('/users/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data, favourite_color=form.favourite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favourite_color.data = ''
        flash('User added Successfully')
    our_users=Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


@app.route('/')
def index():
    form = UserForm()
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


@app.route('/name', methods=['GET','POST'])
def name():
    name = None
    form = NamerForm()
    # validate form
    if form.validate_on_submit():
        name =form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully.")
        
    return render_template('name.html', 
                            name=name, 
                            form=form
                        )


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        app.run(debug=True)