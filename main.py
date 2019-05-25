from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloging@localhost:8889/blogz'

app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(15))
    body = db.Column(db.String(300))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    return redirect('/blog')


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


    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        blog_title_error = ""
        blog_body_error = ""

        if blog_title != "" and blog_body != "":
            new_blog = Blog(blog_title, blog_body)
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





if __name__ == '__main__':
    app.run()