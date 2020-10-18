@app.route('/add_article', methods=["POST","GET"])
def add_article():

    print(session['logged_in'])
    if session['logged_in']==True:
        form=ArticleForm(request.form)
        if request.method=='POST' and form.validate():
            title=form.title.data
            body=form.body.data
            create_date = date.today()
            publish=form.publish.data

            user_logged = User.query.first()
            print(user_logged)

            #item = Items(
            #    title=title,
            #    body=body,
            #    author=user(username=session['username']),
            #    publish=publish,
            #    create_date=create_date

            #)
            #db.session.add(item)
            #db.session.commit()

            flash('Wpis stworzony','success')
            return redirect(url_for('dashboard'))

        print(form)
        return render_template('add_article.html',form=form)
    else:
        flash('Brak autoryzacji, proszę się zalogować', 'danger')
        return redirect(url_for('login'))


@app.route('/edit_article/<string:id>', methods=['GET','POST'])
def edit_article(id):

    result=Items.query.filter_by(id=id).all()
    if len(result)>0:

        article = Items.query.filter_by(id=id).first()
        form=ArticleForm(request.form)

        form.title.data = article.title
        form.body.data = article.body
        form.publish.data = article.publish

        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            publish=request.form.get('publish')
            create_date = date.today()


            if publish != None:
                publish=1
            else:
                publish=0

            article.title = title
            article.body = body
            article.publish = publish
            article.create_date=create_date
            db.session.commit()

            flash("Wpis zaktualizowany", "success")

            return redirect(url_for('dashboard'))

        return render_template('edit_article.html', form=form)
    else:
        msg="Nie znaleziono wpisu"
    return render_template('articles.html',msg=msg)

