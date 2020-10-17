from flask import Flask, render_template,flash, redirect, request, url_for, session
from wtforms import Form,StringField,TextAreaField,PasswordField, BooleanField, validators
from passlib.hash import sha256_crypt
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

# models
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(200), index=True, unique=True)
    username = db.Column(db.String(100), index=True, unique=True)
    password = db.Column(db.String(128))


class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.String(500), index=True, unique=False)
    author= db.Column(db.String(100), index=True, unique=True)
    create_date = db.Column(db.String(128))
    publish= db.Column(db.String(2), unique=False)


migrate = Migrate(app, db)

# registration form
class RegisterForm(Form):
    name=StringField('Imię i nazwisko ',[validators.Length(min=1,max=50)])
    username = StringField('Nazwa użytkownika', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Hasło', [validators.data_required(), validators.equal_to('confirm', message='password do not match')])
    confirm = PasswordField('Potwierdź hasło')

# blog form
class ArticleForm(Form):
    title=StringField('Tytuł',[validators.Length(min=1,max=50)])
    body = TextAreaField('Treść', [validators.Length(min=30)])
    publish =BooleanField('Publikacja')


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=="POST" and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))

        # adding user to database
        user = User(
            name=name,
            email=email,
            username=username,
            password=password,

        )
        db.session.add(user)
        db.session.commit()
        flash('Jesteś już zarejestrowany - możesz się logować', 'success')
        return redirect(url_for("index"))

    return render_template('register.html', form=form)

'''  sql light code
        # create cursor
        conn = create_connection()
        c = conn.cursor()

        # execute
        c.execute("INSERT INTO users (name, email, username, password) VALUES (?,?,?,?)", (name,email,username,password))

        #commit to DB

        conn.commit()

        # close connection
        conn.close()
'''






# user login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=="POST":
        # get form fields
        username=request.form['username']
        password_candidate=request.form['password']

        data = User.query.filter_by(username=username).first()


        if data:
            password=data.password



            # compare password

            if sha256_crypt.verify(password_candidate, password):
                app.logger.info('Password matched')

                session['logged_in']=True
                session['username']=username
                flash('Jesteś już zalogowany', 'success')
                return redirect(url_for('dashboard'))

            else:
                error='Błedne dane logowania'
                return render_template('login.html',error=error)
                #conn.close()


        else:
            error="Użytkownik nie istnieje.Proszę się zarejestrować"
            return render_template('login.html',error=error)



    return render_template('login.html')

'''sql light code
        conn = create_connection()
        # create cursor
        c = conn.cursor()

        # get user by username
        # execute

        result=c.execute("SELECT * FROM users WHERE username=?", (username,))

        data = c.fetchone()
'''




@app.route('/')
def index():
    articles = Items.query.all()

    if len(articles)>0:
        return render_template('index.html', articles=articles)

    msg = "Nie ma żadnych wpisów"
    return render_template('index.html', msg=msg)



'''
    
 
    # sql light code -create cursor
        conn = create_connection()
        # create cursor
        c = conn.cursor()

        # get articles

        result = c.execute("SELECT * from items")

    #if result:

    
        #articles = c.fetchall()

    #return render_template('index.html', articles=articles)
else:
        msg = "Nie ma żadnych wpisów"
    return render_template('index.html', msg=msg)


        #conn.close()
'''




@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    '''# create cursor
    conn = create_connection()
    # create cursor
    c = conn.cursor()

    # get articles

    result = c.execute("SELECT * from items")
    '''

    result=len(Items.query.all())
    if result>0:
        # articles = c.fetchall()
        articles = Items.query.all()

        return render_template('articles.html', articles=articles)
    else:
        msg="Nie znaleziono wpisów"
    return render_template('articles.html',msg=msg)

    #conn.close()

@app.route('/edit_article/<string:id>', methods=['GET','POST'])
def edit_article(id):
    '''# create cursor
    conn = create_connection()
    # create cursor
    c = conn.cursor()

    # get articles

    result = c.execute("SELECT * from items WHERE id=?", (id,))


    '''

    result=Items.query.filter_by(id=id).all()
    if len(result)>0:
        #article = c.fetchone()
        article = Items.query.filter_by(id=id).first()
        form=ArticleForm(request.form)

        #form.title.data=article[1]
        #form.body.data=article[2]
        #form.publish.data=article[5]

        form.title.data = article.title
        form.body.data = article.body
        form.publish.data = article.publish

        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            publish=request.form.get('publish')
            create_date = date.today()

           # print(publish)
            if publish != None:
                publish=1
            else:
                publish=0

            article.title = title
            article.body = body
            article.publish = publish
            article.create_date=create_date
            db.session.commit()

            #print(publish)


            # create cursor
           # conn = create_connection()
            #c = conn.cursor()




            '''c.execute("UPDATE items SET title=?, body =?, author =?, create_date =?, publish =? WHERE id=?",(title,body,session['username'],create_date,publish,id))
            conn.commit()
            conn.close()
            '''
            flash("Wpis zaktualizowany", "success")

            return redirect(url_for('dashboard'))

        return render_template('edit_article.html', form=form)
    else:
        msg="Nie znaleziono wpisu"
    return render_template('articles.html',msg=msg)




@app.route('/delete_article/<string:id>', methods=['POST'])
def delete_article(id):
    '''# create cursor
    conn = create_connection()
    # create cursor
    c = conn.cursor()

    # delete article

    result = c.execute("DELETE from items WHERE id=?", (id,))
    conn.commit()
    conn.close()'''

    article = Items.query.filter_by(id=id).first()
    db.session.delete(article)
    db.session.commit()

    flash("Wpis usunięty", "success")

    return redirect(url_for('dashboard'))







@app.route('/articles/<string:id>/')
def article(id):
    '''
    # create cursor
    conn = create_connection()
    # create cursor
    c = conn.cursor()

    # get article

    result = c.execute("SELECT * from items WHERE id=?",(id,))
    '''
    result=Items.query.filter_by(id=id).all()


    if len(result)>0:
        #article = c.fetchone()
        article = Items.query.filter_by(id=id).first()

        return render_template('article.html', article=article)

    return render_template('article.html',id=id)

@app.route('/dashboard')
def dashboard():
    if session['logged_in']==True:

        '''#create cursor
        conn = create_connection()
        # create cursor
        c = conn.cursor()

        # get articles

        result = c.execute("SELECT * from items")
        '''
        result=Items.query.all()
        if len(result)>0:
           # articles=c.fetchall()
           articles = Items.query.all()
           return render_template('dashboard.html', articles=articles)
        else:
            message='Nie znaleziono artykułu'
            return render_template('dashboard.html', msg=message)

        #conn.close()
    else:
        flash('Brak autoryzacji, proszę się zalogować', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    session['logged_in'] = False
    flash('Jesteś wylogowany', 'success')
    return redirect(url_for('login'))


@app.route('/add_article', methods=["POST","GET"])
def add_article():
    if session['logged_in']==True:
        form=ArticleForm(request.form)
        if request.method=='POST' and form.validate():
            title=form.title.data
            body=form.body.data
            create_date = date.today()
            publish=form.publish.data

            '''#create cursor
            conn = create_connection()
            c = conn.cursor()
            c.execute("INSERT INTO items(title,body,author,publish, create_date) VALUES (?,?,?,?,?)", (title,body, session['username'],publish, create_date))
            conn.commit()
            conn.close()'''

            item = Items(
                title=title,
                body=body,
                author=session['username'],
                publish=publish,
                create_date=create_date

            )
            db.session.add(item)
            db.session.commit()
            flash('Wpis stworzony','success')
            return redirect(url_for('dashboard'))

        return render_template('add_article.html',form=form)
    else:
        flash('Brak autoryzacji, proszę się zalogować', 'danger')
        return redirect(url_for('login'))

# próba


@app.route('/render_article/<string:id>', methods=["POST", "GET"])
def render_article(id):
    if id == "add":
        if session['logged_in'] == True:
            form = ArticleForm(request.form)
            if request.method == 'POST' and form.validate():
                title = form.title.data
                body = form.body.data
                create_date = date.today()
                publish = form.publish.data

                item = Items(
                    title=title,
                    body=body,
                    author=session['username'],
                    publish=publish,
                    create_date=create_date

                )
                db.session.add(item)
                db.session.commit()
                flash('Wpis stworzony', 'success')
                return redirect(url_for('dashboard'))

            return render_template('entry_form.html', form=form,type="add")
        else:
            flash('Brak autoryzacji, proszę się zalogować', 'danger')
            return redirect(url_for('login'))
    else:
        result = Items.query.filter_by(id=id).all()
        if len(result) > 0:

            article = Items.query.filter_by(id=id).first()
            form = ArticleForm(request.form)

            form.title.data = article.title
            form.body.data = article.body
            form.publish.data = article.publish

            if request.method == 'POST':
                title = request.form['title']
                body = request.form['body']
                publish = request.form.get('publish')
                create_date = date.today()

                # print(publish)
                if publish != None:
                    publish = 1
                else:
                    publish = 0

                article.title = title
                article.body = body
                article.publish = publish
                article.create_date = create_date
                db.session.commit()

                flash("Wpis zaktualizowany", "success")

                return redirect(url_for('dashboard'))

            return render_template('entry_form.html', form=form,type="edit")
        else:
            msg = "Nie znaleziono wpisu"
        return render_template('articles.html', msg=msg)


if __name__=='main':
    app.run(debug=True)
