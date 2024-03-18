
from datetime import date
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import login_user, logout_user, LoginManager, login_required, current_user, UserMixin
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os


# create a flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/users_db'
app.config['SECRET_KEY'] = 'xtransparent zozilla'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ckeditor = CKEditor(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        
        post.searched = form.searched.data
        
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', 
                                        form=form, searched= post.searched, posts=posts)



@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 18:
        return render_template('admin.html')
    else:
        flash('Sorry only admin can access.')
        return redirect(url_for('dashbaord'))


@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashbaord():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        # set uid
        pic_name = str(uuid.uuid1()) + '_' + pic_filename
        name_to_update.profile_pic = pic_name
        
        try:
            db.session.commit()
            flash('User updated Successfully.')
            return render_template('dashboard.html', 
                                    form=form, 
                                    name_to_update = name_to_update)
        except:
            flash('Error. something went wrong')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id )
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
    
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login Successfull')
                return redirect(url_for('dashbaord'))
            else:
                flash('Wrong Password. Please Try Again.')        
        else:
            flash('Thats User Doesnt Exists.')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You are Logged Out!')
    return redirect(url_for('login'))

# json code
@app.route('/date')
def get_current_date():
    goal_car = {
        "brand": "Mercedes",
        "model": "cls a-limopusine",
        "price": "55896785"
    }
    return goal_car


@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)
    
    
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash('Post has been Updated.')
        return redirect(url_for('post', id=post.id))  
    
    if current_user.id == post.poster_id:   
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash('You are Not Authorized to Update This Post.')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:              
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            
            flash('Blog has been Deleted Successfully!')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        except:
            flash('there was a problem deleteing a post , try again.')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
    else:
        flash('You are not Authorized To delete.')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)
        


@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title= form.title.data, content=form.content.data ,poster_id=poster, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''
        
        db.session.add(post)
        db.session.commit()
        
        flash('Blog Added Successfully!')
    return render_template('add_post.html', form=form)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:        
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
    else:
        flash('Sorry! You cant delete this user.')
        return redirect(url_for('dashboard'))
        


@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User updated Successfully.')
            return render_template('update.html', 
                                    form=form, 
                                    name_to_update = name_to_update)
        except:
            flash('Error. something went wrong')
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id )
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
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, 
                            favourite_color=form.favourite_color.data,
                            password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
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
    
    
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(200))
    posts = db.relationship('Posts', backref='poster')
    
    
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
    
    
class Posts(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(125), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # author = db.Column(db.String(125))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug =  db.Column(db.String(255))
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        app.run(debug=True)