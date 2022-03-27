
from application import app, db, api
from flask import Response, flash, jsonify, redirect, render_template, request, json, url_for, session
from application.forms import LoginForm, RegisterForm
from application.models import User, Course, Enrollment
from flask_restx import Resource
#from application.static import courseData
#----------API----------------------------
@api.route('/api', '/api/')
class GetAndPost(Resource):
#GET all
    def get(self):
        return jsonify(User.objects.all())

#POST
    def post(self):
        data = api.payload
        user = User(user_id=data['user_id'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'])

        user.set_password(data['password'])
        user.save()
        return jsonify(User.objects(user_id = data['user_id']))

@api.route('/api/<idx>')
class GetUpdateDelete(Resource):
#GET one
    def get(self, idx):
        return jsonify(User.objects(user_id=idx))

#PUT
    def put(self, idx):
        data=api.payload
        User.objects(user_id=idx).update(**data)
        return jsonify(User.objects(user_id=idx))

#DELETE
    def delete(self, idx):
        User.objects(user_id=idx).delete()
        return jsonify(f'User {idx} is deleted')

#-----------APP----------------------------
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    
    with open('application/static/text1.txt') as txt:
        cont = txt.read()
    return render_template('index.html', active_nav='index', page_text=cont)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #if dont want logined user to get to this page:
    if session.get('username'):
        return redirect(url_for('index'))
    frm = LoginForm()
    if frm.validate_on_submit():

        frm_email = frm.email.data
        frm_password = frm.password.data

        user = User.objects(email=frm_email).first()
        ## we use first to get one object, otherwise we'll get array[]
        ##if user and frm_password == user.password:
        if user and user.get_password(frm_password):
            flash(f'{user.first_name}, you are successfuly logged in.', 'success')
            session['user_id'] = user.user_id
            session['username'] = user.first_name
            return redirect('/index')
        else:
            flash('Try again', 'danger')
    return render_template('login.html', title='Login', active_nav='login', form=frm)

@app.route('/register', methods=['GET', 'POST'])
def register():
    frm = RegisterForm()

    if frm.validate_on_submit():
        user_id = User.objects.count() + 1
        frm_email = frm.email.data
        frm_password = frm.password.data
        frm_first_name = frm.first_name.data
        frm_last_name = frm.last_name.data

        user = User(user_id=user_id,
            email=frm_email,
            first_name=frm_first_name,
            last_name=frm_last_name)

        user.set_password(frm_password)
        user.save()

        flash('You are registered.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', title='New User Registration', form=frm, active_nav='register')



@app.route('/logout')
def logout():
    session['user_id'] = False
    session.pop('username', None)
    return redirect(url_for('index'))



@app.route('/courses/')
@app.route('/courses/<term_year>')
def courses(term_year='Spring 2022'):
    # read from DB
    classes = Course.objects.order_by('-courseID') # '-' to sort inverse direction

    return render_template('courses.html', course_data=classes, active_nav='courses', year=term_year)


@app.route('/enrollment', methods=['GET', 'POST'])
def enrollment():
    #we show page only if user is logged in
    if not session.get('username'):
        return redirect(url_for('login'))

    get_user_id = session.get('user_id')

    ##  to receive data from GET method in courses.html, using name in <input>
    getID = request.form.get('courseID')
    getTitle = request.form.get('title')
    #getTitle = request.form['title'] ## two ways to access data from form. But this is crashing if no 'title'
    getTerm = request.form.get('term')

    if getID:
        if Enrollment.objects(user_id=get_user_id, courseID=getID):
            flash(f'You are arleady registered in {getTitle}.', 'danger')
            return redirect(url_for('courses'))
        else:
            # add to DB
            Enrollment(user_id=get_user_id, courseID=getID).save()
            flash(f'You are enrolled in {getTitle}.', 'success')
## it is code generated in MongodbCompass:
    classes = list(User.objects.aggregate(*[
        {
            '$lookup': {
                'from': 'enrollment', 
                'localField': 'user_id', 
                'foreignField': 'user_id', 
                'as': 'r1'
            }
        }, {
            '$unwind': {
                'path': '$r1', 
                'includeArrayIndex': 'r1_id', 
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$lookup': {
                'from': 'course', 
                'localField': 'r1.courseID', 
                'foreignField': 'courseID', 
                'as': 'r2'
            }
        }, {
            '$unwind': {
                'path': '$r2', 
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$match': {
                'user_id': get_user_id
            }
        }, {
            '$sort': {
                'courseID': 1
            }
        }
    ]))




    return render_template('enrollment.html', active_nav='enrollment', title='Enrollment',
        classes=classes
        )






@app.route('/user')
def user():
    ##add users for test:
    # User(user_id=1, first_name='First', last_name='firstSurname', email='first@example.com', password='1234').save()
    # User(user_id=2, first_name='Second', last_name='secondSurname', email='second@example.com', password='1234').save()

    users=User.objects.all()

    return render_template('user.html', users=users)