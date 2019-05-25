from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloging@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(15))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            flash("Logged in")

            return redirect('/')

        else:
            flash("Password incorrect or User does not exist.", "error")

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(name, email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            return '<h1>Duplicate user</h1>'
    
    return render_template('register.html')



@app.route('/')
def index():
    return redirect('/all-users')


@app.route('/blog', methods=['GET'])
def all_blogs():

    if request.args:
        selected_blog = request.args.get("id")
        right_blog = Blog.query.get(selected_blog)
        return render_template('blog_page.html', title="blog-page", blog=right_blog)
    else:
        blogs = Blog.query.all()

        return render_template('blog.html', title="Blogs", blogs=blogs)


@app.route('/postblog', methods=['POST', 'GET'])
def post_blog():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        blog_title_error = ""
        blog_body_error = ""

        if blog_title != "" and blog_body != "":
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
        else:
            if blog_title == "" and blog_body == "":
                blog_title_error = "Title required."
                blog_body_error = "Blog body required."

            elif blog_title == "":
                blog_title_error = "Title required."
                blog_body = request.form['blog-body']
            else:
                if blog_body == "":
                    blog_body_error = "Blog body required."
                    blog_title = request.form['blog-title']

            return render_template('postblog.html', title="Post-Blog", 
            blog_title_error=blog_title_error,
            blog_body_error=blog_body_error,
            blog_title=blog_title,
            blog_body=blog_body)


    return render_template('postblog.html', title="Post-Blog")


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/all-users', methods=['POST','GET'])
def all_users():

    if request.args:
        selected_user = request.args.get("owner_id")
        # user = User.query.filter_by(id=selected_user).first()
        by_user = Blog.query.filter_by(owner=selected_user).all()
        return render_template('by_user.html', title="User Blogs", blogs=by_user)
    else:
        users = User.query.all()

        return render_template('all_users.html', title="All Users",
        users=users)


if __name__ == '__main__':
    app.run()