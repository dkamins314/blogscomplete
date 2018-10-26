from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app= Flask (__name__)
app.config['DEBUG']= True
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://blogs:abc123@localhost:8889/blogs'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key='56ka52dh10WQOPHT$%$%$'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))


    def __init__(self, title, body, owner):
        self.title = title
        self.body= body
        self.owner= owner
        
      
    
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_name= db.Column(db.String(120), unique=True)
    password=db.Column(db.String(120))
    blogs= db.relationship('Blog', backref='owner')

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login','register', 'all_blogs', 'index']
    if request.endpoint not in allowed_routes and 'user_name' not in session:
        return redirect('/login')
       



@app.route('/register', methods =['POST','GET'])
def register():
     if request.method == 'POST':
        user_name =request.form['user_name']
        password = request.form['password']
        verify = request.form['verify']
        if len(user_name) == 0:
            flash("The name field was left blank.", 'error')
            return render_template('/register')
        else:
            user_name = user_name
        if len(password) == 0:
            flash('The password field was left blank.', 'error')
            return render_template("register.html", user_name = user_name, password='', verify='')
        else:
            password = password
        if len(verify) == 0:
            flash('The verify password field was left blank.', 'error')
            return render_template("register.html", user_name = user_name, password='', verify='')
        

        if len(user_name) != 0:
            if len(user_name) < 5 or len(user_name) > 40 or ' ' in user_name:
                # minimum user name
                flash('User_name must be between 4 and 20 characters long, cannot contain spaces.', 'error')
                return  redirect('/register')
            else:
                user_name = user_name

        if len(password) != 0:
            if len(password) < 4 or len(password) > 19 or ' ' in password:
                flash("The password must be between 4 and 19 characters long and cannot contain spaces.", 'error')
                return  render_template("register.html", user_name = user_name, password='', verify='')
            else:
                password = password

        for char, letter in zip(password, verify):
            if char != letter:
                flash('The verifying password does not match the password.Please try again.', 'error')
                return render_template("register.html", user_name = user_name, password='', verify='')
            else:
                verify = verify
                password = password

        if user_name and password and verify:
      
            existing_user = User.query.filter_by(user_name= user_name).first()

        if not existing_user:
            new_user = User(user_name, password)
            db.session.add(new_user)
            db.session.commit()
            session['user_name'] =user_name
            return redirect('/all_blogs')
        else:
    
            flash('Duplicate user, please login')

            return render_template('login.html')
     return render_template('register.html')


@app.route('/login', methods =['POST','GET'] )
def login():
    if request.method == 'POST':
        user_name =request.form['user_name']
        password = request.form['password']
        user = User.query.filter_by(user_name= user_name).first()
        if user and user.password == password:
            session['user_name'] =user_name
            flash("Logged In!")
            return redirect('/new_blog')
        else:
            flash( 'User password is incorrect, or user is not registered','error')
            return  redirect('/login')          
    return render_template('login.html')


@app.route('/', methods =['POST','GET'] )
def index():
    return redirect('/home')


@app.route('/Home', methods =['POST','GET'] )
def home():
    users = User.query.all()
    return render_template('Home.html', users=users)

 
@app.route('/all_blogs', methods =['POST','GET'] )
def render_all_blogs():
    blogs = Blog.query.all()
    return render_template('all_blogs.html', blogs=blogs) 

  
@app.route('/blog', methods=['POST','GET'])
def display_blogs():
   blog_id =request.args.get('id') 
   if (blog_id):
      blog=Blog.query.get(blog_id)
      return render_template('single_blog.html', title="Blog Title", blog= blog) 
   else:
        all_blogs = Blog.query.all() 

        return render_template('all_blogs.html', title="All Blogs", all_blogs=all_blogs)


@app.route('/single_user', methods=['POST','GET'])   
def render_su():
    single_blog = request.args.get("id")
    if single_blog:
       blog = Blog.query.get(single_blog)
       return render_template("single_user.html",title = user.user_name + "'s Posts!", blog= user_blog)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="All Blog Posts!", blogs=blogs)


@app.route('/single_user_all', methods=['POST','GET'])
def render_sua():
    user_id= request.args.get('id')
    user = user_id
    if (user_id):
       user = User.query.filter_by(id = user_id).first()  
       user_blogs = Blog.query.filter_by(owner_id=user_id).all()
      
    return render_template("single_user_all.html", title =user.user_name + "'s Posts!", user_blogs=user_blogs)      

@app.route('/all_users', methods=['POST','GET'])   
def render_all_users():
        user = User.query.all()
        return render_template("all_users.html", user=user) 

@app.route('/new_blog', methods=['Post', 'GET'] )
def new_blog_entry():
    owner = User.query.filter_by(user_name= session['user_name']).first()
    
    
    if request.method == 'POST':
        blog_title = request.form ['title'] 
        blog_body = request.form ['body']
        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        all_blogs = Blog.query.all()
        return render_template('all_blogs.html',title="All Blogs", blogs=all_blogs)

    return render_template('new_blog.html')
        #else:
          #  flash("Please check your entry for errors or missing fields. Both title and body are required")
           # return render_template('new_blog.html', title = "Create new blog entry", blog_title = blog_title,
                   #blog_body = blog_body)
    #else:
        #return render_template('new_blog.html', title= "Create new blog")




@app.route('/logout')
def logout():
    del session['user_name']
    return redirect('/login')

        
   



if __name__ == '__main__':
    app.run()