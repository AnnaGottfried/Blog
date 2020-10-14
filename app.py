from flask import Flask, render_template,flash, redirect, request, url_for, session, logging
from wtforms import Form,StringField,TextAreaField,PasswordField, validators
from passlib.hash import sha256_crypt
import sqlite3
import os
from datetime import date




app=Flask(__name__)
app.secret_key = "super secret key"
# inna metoda

def create_connection():
    db_abs_path = os.path.dirname(os.path.realpath(__file__)) + 'db/users.db'
    conn = sqlite3.connect('db/users.db', check_same_thread=False)
    return conn



class RegisterForm(Form):
    name=StringField('Imię i nazwisko ',[validators.Length(min=1,max=50)])
    username = StringField('Nazwa użytkownika', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Hasło', [validators.data_required(), validators.equal_to('confirm', message='password do not match')])
    confirm = PasswordField('Potwierdź hasło')

# article form
class ArticleForm(Form):
    title=StringField('Tytuł',[validators.Length(min=1,max=50)])
    body = TextAreaField('Treść', [validators.Length(min=30)])


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=="POST" and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        conn = create_connection()
        c = conn.cursor()

        # execute
        c.execute("INSERT INTO users (name, email, username, password) VALUES (?,?,?,?)", (name,email,username,password))

        #commit to DB

        conn.commit()

        # close connection
        conn.close()

        flash('Jesteś już zarejestrowany - możesz się logować', 'success')
        return redirect(url_for("index"))

    return render_template('register.html', form=form)

# user login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=="POST":
        # get form fields
        username=request.form['username']
        password_candidate=request.form['password']

        conn = create_connection()
        # create cursor
        c = conn.cursor()

        # get user by username
        # execute

        result=c.execute("SELECT * FROM users WHERE username=?", (username,))

        data = c.fetchone()

        if data:
            password=data[4]



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
                conn.close()


        else:
            error="Użytkownik nie istnieje.Proszę się zarejestrować"
            return render_template('login.html',error=error)



    return render_template('login.html')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    # create cursor
    conn = create_connection()
    # create cursor
    c = conn.cursor()

    # get articles

    result = c.execute("SELECT * from items")
    if result:
        articles = c.fetchall()

        return render_template('articles.html', articles=articles)
    else:
        msg="Nie znaleziono wpisów"
    return render_template('articles.html',msg=msg)

    conn.close()

@app.route('/edit_article/<string:id>', methods=['GET','POST'])
def edit_article(id):
    # create cursor
    conn = create_connection()
    # create cursor
    c = conn.cursor()

    # get articles

    result = c.execute("SELECT * from items WHERE id=?", (id,))
    if result:
        article = c.fetchone()
        form=ArticleForm(request.form)

        form.title.data=article[1]
        form.body.data=article[2]

        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            create_date = date.today()


            # create cursor
           # conn = create_connection()
            c = conn.cursor()

            c.execute("UPDATE items SET title=?, body =?, author =?, create_date =? WHERE id=?",(title,body,session['username'],create_date,id))
            conn.commit()
            conn.close()
            flash("Wpis zaktualizowany", "success")

            return redirect(url_for('dashboard'))

        return render_template('edit_article.html', form=form)
    else:
        msg="Nie znaleziono wpisu"
    return render_template('articles.html',msg=msg)




@app.route('/delete_article/<string:id>', methods=['POST'])
def delete_article(id):
    # create cursor
    conn = create_connection()
    # create cursor
    c = conn.cursor()

    # delete article

    result = c.execute("DELETE from items WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Wpis usunięty", "success")

    return redirect(url_for('dashboard'))







@app.route('/articles/<string:id>/')
def article(id):
    # create cursor
    conn = create_connection()
    # create cursor
    c = conn.cursor()

    # get article

    result = c.execute("SELECT * from items WHERE id=?",(id,))
    if result:
        article = c.fetchone()

        return render_template('article.html', article=article)

    return render_template('article.html',id=id)

@app.route('/dashboard')
def dashboard():
    if session['logged_in']==True:

        #create cursor
        conn = create_connection()
        # create cursor
        c = conn.cursor()

        # get articles

        result = c.execute("SELECT * from items")
        if result:
            articles=c.fetchall()

            return render_template('dashboard.html', articles=articles)
        else:
            message='Nie znaleziono artykułu'
            return render_template('dashboard.html', msg=message)

        conn.close()
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

            #create cursor
            conn = create_connection()
            c = conn.cursor()
            c.execute("INSERT INTO items(title,body,author,create_date) VALUES (?,?,?,?)", (title,body, session['username'], create_date))
            conn.commit()
            conn.close()
            flash('Wpis stworzony','success')
            return redirect(url_for('dashboard'))

        return render_template('add_article.html',form=form)
    else:
        flash('Brak autoryzacji, proszę się zalogować', 'danger')
        return redirect(url_for('login'))





if __name__=='main':
    app.run(debug=True)
