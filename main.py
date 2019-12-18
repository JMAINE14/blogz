from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cheese@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'kjlfjweoifj'


def not_valid(inpt):
    if len(inpt) < 3 or len(inpt) > 20:
        return True
    elif ' ' in inpt:
        return True
    return False

def same_user(username):
    if User.query.filter_by(username=username).first():
        return True
    return False


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def login_required():
    allowed_routes = ['login', 'signup', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():

    username = ''
    username_error = ''
    password_error = ''
    password = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        #if not_valid(username) or not username:
        if not_valid(username):
            username_error = "That's not a valid username"
            username = ''

        #if not_valid(password) or not password:
        if not_valid(password):
            password_error = "That's not a valid password"
            password = ''
            
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/blogs')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            password = ''

    return render_template('login.html', username_error=username_error, password_error=password_error, username=username, password=password)


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    username = ''
    username_error = ''
    password_error = ''
    verify_error = ''
    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
       
        if not_valid(username):
            username_error = "That's not a valid username"
            username = ''
   
        if not_valid(password):
            password_error = "That's not a valid password"
            password = ''

        if password != verify:
            verify_error = "Password doesn't match"
            verify = ''
        if same_user(username):
                username_error = "Duplicate username"
                username = '' 
        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not (username_error or password_error or verify_error or existing_user):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blogs')

    return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error, username=username)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    title_error = ''
    body_error = ''
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        blog_post = Blog(title, body, owner)
        #user_post = User(username, password)
        db.session.add(blog_post)
        db.session.commit()

        if not title:
            title_error = "Input title"
            title = ''
        
        if not body:
            body_error = "Input body"
            body = ''

        if (title_error or body_error):
            return render_template('newpost.html', title_error=title_error, body_error=body_error)

        return render_template('viewpost.html', blog=blog_post)

    return render_template('newpost.html')
# @app.route('/', methods=['GET'])
@app.route('/blogs', methods=['GET'])
def blog():

    blog_id = request.args.get('id')
    blog_username = request.args.get('username')
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('viewpost.html', blog=blog)
    if blog_username:
        user = User.query.filter_by(username=blog_username).first()
        blogs = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('mainpage.html', blogs=blogs)

    blogs = Blog.query.all()
    return render_template("mainpage.html", blogs=blogs)

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

# @app.route('/')
# def index():



#     owner = User.query.filter_by(username=session['username']).first()

#     if request.method == 'POST':
#         user_name = request.form['user']
#         new_user = User(user_name, owner)
#         db.session.add(new_user)
#         db.session.commit()
# #replacing users with blogs....
#     blogs = User.query.filter_by(completed=False,owner=owner).all()
#     completed_blogs = User.query.filter_by(completed=True,owner=owner).all()
#     return render_template('index.html',title="Home!", 
#         Blogs=blogs, completed_Blogs=completed_Blogs)

@app.route('/delete-user', methods=['POST'])
def delete_user():

    user_id = int(request.form['user-id'])
    user = User.query.get(user_id)
    user.completed = True
    db.session.add(user)
    db.session.commit()

    return redirect('/blog')

if __name__ == '__main__':
    app.run()
