from flask import Flask, render_template,flash, redirect, request, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,PasswordField, BooleanField, validators
from passlib.hash import sha256_crypt
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms.validators import DataRequired

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
    articles = db.relationship("Items", backref='author')


class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.String(500))
    author_id= db.Column(db.Integer,db.ForeignKey('user.id'))
    create_date = db.Column(db.String(128))
    publish= db.Column(db.Boolean(), default=False, nullable=True)


migrate = Migrate(app, db)

# registration form
class RegisterForm(FlaskForm):
    name=StringField('Imię i nazwisko ',[validators.Length(min=1,max=50)])
    username = StringField('Nazwa użytkownika', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Hasło', [validators.data_required(), validators.equal_to('confirm', message='Hasło się nie zgadza')])
    confirm = PasswordField('Potwierdź hasło')

# blog form
class ArticleForm(FlaskForm):
    title=StringField('Tytuł',validators=[DataRequired()])
    body = TextAreaField('Treść', validators=[DataRequired()])
    publish =BooleanField('Publikacja')


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)

    result_name = User.query.filter_by(name=form.name.data).all()
    result_username = User.query.filter_by(username=form.username.data).all()
    result_email = User.query.filter_by(email=form.email.data).all()

    result= len(result_name) +len(result_username)+len(result_email)

    errors = None

    if request.method=="POST" and  result==0:
        if form.validate_on_submit():

            name=form.name.data
            email=form.email.data
            username=form.username.data
            password=sha256_crypt.encrypt(str(form.password.data))

        # adding user to database if the user does not exist
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
        else:
            errors = form.errors
            return render_template('register.html', errors=errors, form=form)

    else:
        if len(result_name)>0:
            flash('Użytkownik o tym imieniu i nazwisku już istnieje', 'danger')
        if len(result_username)>0:
            flash('Nazwa użytkownika taka już istnieje', 'danger')

        if len(result_email)>0:
            flash('Email taki już istnieje', 'danger')

        errors=form.errors
        return render_template('register.html', errors=errors,form=form)


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



        else:
            error="Użytkownik nie istnieje.Proszę się zarejestrować"
            return render_template('login.html',error=error)



    return render_template('login.html')


@app.route('/')
def index():
    articles = Items.query.all()

    if len(articles)>0:
        return render_template('index.html', articles=articles)

    msg = "Nie ma żadnych wpisów"
    return render_template('index.html', msg=msg)




@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():

    result=len(Items.query.all())
    if result>0:
        # articles = c.fetchall()
        articles = Items.query.all()

        return render_template('articles.html', articles=articles)
    else:
        msg="Nie znaleziono wpisów"
    return render_template('articles.html',msg=msg)



@app.route('/delete_article/<string:id>', methods=['POST'])
def delete_article(id):

    article = Items.query.filter_by(id=id).first()
    db.session.delete(article)
    db.session.commit()

    flash("Wpis usunięty", "success")

    return redirect(url_for('dashboard'))


@app.route('/articles/<string:id>/')
def article(id):
    result=Items.query.filter_by(id=id).all()


    if len(result)>0:

        article = Items.query.filter_by(id=id).first()

        return render_template('article.html', article=article)

    return render_template('article.html',id=id)

@app.route('/dashboard')
def dashboard():
    if session['logged_in']==True:

        result=Items.query.all()
        if len(result)>0:

           articles = Items.query.all()
           return render_template('dashboard.html', articles=articles)
        else:
            message='Nie znaleziono artykułu'
            return render_template('dashboard.html', msg=message)

    else:
        flash('Brak autoryzacji, proszę się zalogować', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    session['logged_in'] = False
    flash('Jesteś wylogowany', 'success')
    return redirect(url_for('login'))



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


                user_logged = User.query.filter_by(username=session['username']).first()
                print(user_logged.username)

                item = Items(
                    title=title,
                    body=body,
                    author=user_logged,
                    publish=publish,
                    create_date=create_date

                )
                db.session.add(item)
                db.session.commit()
                flash('Wpis stworzony', 'success')
                return redirect(url_for('dashboard'))

            else:
                errors = form.errors
                return render_template('entry_form.html', form=form,errors=errors, type="add")
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

            errors = None

            if request.method == 'POST':

                print(form.validate_on_submit())

                if form.validate_on_submit():

                    title = request.form['title']
                    body = request.form['body']
                    publish = request.form.get('publish')
                    create_date = date.today()


                    if publish != None:
                        publish = 1
                    else:
                        publish = 0

                    article.title = title
                    article.body = body
                    article.publish = publish
                    article.create_date = create_date
                    article.author=User.query.filter_by(username=session['username']).first()
                    db.session.commit()

                    flash("Wpis zaktualizowany", "success")

                    return redirect(url_for('dashboard'))
                else:
                    errors = form.errors
                    return render_template('entry_form.html', errors=errors, form=form, type="edit")

            else:
                errors = form.errors
                return render_template('entry_form.html',errors=errors, form=form,type="edit")
        else:
            msg = "Nie znaleziono wpisu"
            return render_template('articles.html',msg=msg)


if __name__=='main':
    app.run(debug=True)
