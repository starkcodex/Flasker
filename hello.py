from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# create a flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'xtransparent zozilla'

# create 
class NamerForm(FlaskForm):
    name = StringField('Please Enter Your Name:', validators=[DataRequired()])
    submit = SubmitField("Submit")


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
    app.run(debug=True)