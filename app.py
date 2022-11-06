from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash





base_dir = os.path.dirname(os.path.realpath(__file__))

db = SQLAlchemy() 

app = Flask(__name__)


app.config['SECRET_KEY'] = "baby girl"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(base_dir, 'blog.db')
app.config['SQLALCHEMY_DATABASE_MODIFICATIONS'] = False

db.init_app(app)
        
       
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255),nullable=False) 
    last_name = db.Column(db.String(255),nullable=False) 
    email = db.Column(db.String(255),unique=True,nullable=False) 
    password= db.Column(db.String(255),nullable=False) 
    gender = db.Column(db.String(25),nullable=False) 
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    posts = db.relationship('Post', backref="user", passive_deletes=True )
    
def __repr__(self):
    return f"User '{self.first_name}', '{self.last_name}'. '{self.email}' "  

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    
def __repr__(self):
    return f"Post('{self.text}', '{self.date_created}')"    

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


        
        
@app.route("/")
@app.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", posts=posts, user=current_user.email)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!",  category='success')
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist', category='error' )        
                
    return render_template('login.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name =request.form.get('first_name')
        last_name =request.form.get('last_name')
        email =request.form.get('email')
        gender=request.form.get('gender')
        password1 =request.form.get('password1')
        password2=request.form.get('password2')
        
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('Email is already in use.' , category= 'error')
            return redirect(url_for('register'))
        if password1 != password2:
            flash('Password do not match', category='error')
        if len(password1) < 6:
            flash('Password is too short', category='error')
        if len(email) < 4:
            flash('Email is Invalid.', category='error')  
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, gender=gender, password=generate_password_hash(password1, method='sha256'))          
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Successfull!')
            return redirect(url_for('home'))
               
            
    
    return render_template('register.html', user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()   
    return redirect(url_for('home'))


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        
        content = request.form.get("content")
        if len(content)< 1:
            flash("post is too short", category="error")
        else:
            new_post = Post(content=content, author=current_user.id)  
            db.session.add(new_post)
            db.session.commit()
            flash('post created!', category='success')
        
            
            return redirect('home')
               
    return render_template('create_post.html', user=current_user)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    content_to_edit = Post.query.get_or_404(id)
    if request.method == "POST":
        content_to_edit.content = request.form.get("content")
        try:
            db.session.commit()
            return redirect(url_for("home"))
        except:
            flash("There was a problem updating that post.", category="error")
    return render_template('edit.html', content_to_edit=content_to_edit)


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    

    try:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("home"))
    except:
        flash("There was a problem deleting that post. ", category="error")
        




if __name__ == "__main__":
    app.run(debug=True)
    
    
