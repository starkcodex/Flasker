from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask import Flask, render_template, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

from wtforms.widgets import TextArea

# create a flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/users_db'
app.config['SECRET_KEY'] = 'xtransparent zozilla'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# json code
@app.route('/date')
def get_current_date():
    goal_car = {
        "brand": "Mercedes",
        "model": "cls a-limopusine",
        "price": "55896785"
    }
    return goal_car


class Posts(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(125), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(125))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug =  db.Column(db.String(255))
    
    
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title= form.title.data, content=form.content.data ,author=form.author.data, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        
        db.session.add(post)
        db.session.commit()
        
        flash('Blog Added Successfully!')
    return render_template('add_post.html', form=form)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(200))
    
    
    @property
    def password(self):
        raise AttributeError('password is not readable attribute.')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<Name %r>' % self.name
    
    
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    favourite_color = StringField('Favourite Color')
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password must match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# create a form for input 
class PasswordForm(FlaskForm):
    email = StringField('Your Email:', validators=[DataRequired()])
    password_hash = PasswordField('Your Password:', validators=[DataRequired()])
    submit = SubmitField("Submit")


# create a form for input 
class NamerForm(FlaskForm):
    name = StringField('Please Enter Your Name:', validators=[DataRequired()])
    submit = SubmitField("Submit")
    
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User deleted Successfully!')
        our_users=Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash('there was a problem deleteing user.')
        return render_template('add_user.html', form=form, name=name, our_users=our_users)


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
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

    
    
@app.route('/users/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(name=form.name.data, email=form.email.data, 
                            favourite_color=form.favourite_color.data,
                            password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favourite_color.data = ''
        form.password_hash.data = ''
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


@app.route('/test_pw', methods=['GET','POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    
    
    # validate form
    if form.validate_on_submit():
        email =form.email.data
        password = form.password_hash.data
        
        form.email.data = ''
        form.password_hash.data = ''
        
        pw_to_check = Users.query.filter_by(email=email).first()
        
        # flash("Form Submitted Successfully.")
        
        # checked hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)
        
    return render_template('test_pw.html', 
                            email=email, 
                            password=password,
                            form= form,
                            passed = passed,
                            pw_to_check = pw_to_check
                        )


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