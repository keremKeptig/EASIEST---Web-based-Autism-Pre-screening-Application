import os
from datetime import datetime

import requests as requests
from sqlalchemy import desc
from flask import render_template, flash, redirect, url_for, request, session
from EASIEST import app, db, bcrypt
from EASIEST.database import Doctor, Patients, Test, Admin, User
from EASIEST.Forms import RegistrationForm, LoginForm, PatientForm
from EASIEST.fixation import ivt,idt
from EASIEST.feature_generation import screen_find_element, compute_metrics, grid_find_element
from flask_login import login_user, current_user, logout_user, login_required
from flask import Flask, request, render_template, jsonify, send_file
from EASIEST.prediction import insert_user_data
from EASIEST.prediction2 import insert_user_data2
import pandas as pd
import re


@app.route("/", methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route("/dashboard", methods=['GET','POST'])
@login_required
def dashboard(patients=None, tests=None):
    if (isinstance(current_user,Doctor) and current_user.IsValidated==0):
        return render_template('DoctorNotValidated.html')
    elif(isinstance(current_user,Admin)):

        doctors = Doctor.query.all()
        return render_template('AdminDashboard.html', doctors=doctors)
    if (not patients):
        patients = Patients.query.filter_by( doctors_id= current_user.id).all()
        tests={}
        for patient in patients:
            test = Test.query.filter_by(taker=patient).order_by(desc(Test.date)).all()
            tests[patient.name]=test[0]
    form = PatientForm()

    #test_info = Test.query.all()
    #print(test_info)

    if form.validate_on_submit():
        patient = Patients(name=form.Name.data,surname=form.Surname.data,
                      phonenum=form.Tel.data,doctors_id=current_user.id)
        db.session.add(patient)
        db.session.commit()
        test = Test(patient_id=patient.id)
        db.session.add(test)
        db.session.commit()
        flash(f"Your patient is created!","success")
        return redirect(url_for("dashboard"))
    return render_template('dashboard.html', title='Dashboard', patients=patients, form=form,tests=tests)

@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #need to add validations on the email
        search_user_by_email = User.query.filter_by(email=form.Email.data).first()
        search_user_by_username = User.query.filter_by(username=form.Username.data).first()
        search_user_by_phone = User.query.filter_by(phonenum=form.Tel.data).first()

        if search_user_by_email or search_user_by_username or search_user_by_phone:
            flash('User already exists!', 'error')
            return render_template('register.html', form=form, messages='user exists')

        hashed_password = bcrypt.generate_password_hash(form.Password.data).decode('utf-8')
        user = Doctor(name=form.Name.data,surname=form.Surname.data,
                      username=form.Username.data,email=form.Email.data,
                      phonenum=form.Tel.data,adress=form.Address.data,
                      hospital_name=form.Hospital.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account is created!","success")
        return redirect(url_for("login"))
    return render_template('register.html',form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.Email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.Password.data):
            login_user(user,remember=form.Remember.data)
            next_page= request.args.get('next')
            return redirect(next_page) if next_page else  redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account',doctor=current_user)


@app.route('/calibration/<string:id>', methods=['GET', 'POST'])
@login_required
def calibration(id):
    return render_template('calibration.html', id=id)


@app.route('/website/<string:id>', methods=['GET'])
@login_required
def get_index_with_params(id):
    return render_template('main_test_pages.html',id=id)


@app.route('/save_data', methods=['GET','POST'])
@login_required
def save_data():

    # Access the data sent in the request's body
    data = request.get_json()  # get the json data from the post request

    eye_tracking_data = data['eyeTrackingData']  # eye tracking data x, y, clock
    azalma_orani = data['azalmaOrani']  # azalmaOrani value
    padding = data['widthRatio']  # padding value
    test_id = data['testID']  # testID for each page
    user_id = data['id']  # unique user id for each patient generated and fetched

    values = []  # empty values array created for each /save_data endpoint called (each 'Next Button' clicked)

    for data_point in eye_tracking_data:
        values.extend(data_point)  # extending the values array for all gaze points

    # for adjusting the clock part

    first_time = 0
    for i in range(0, len(values), 4):
        if values[i + 3] == test_id:
            first_time = values[i + 2]  # her yeni sayfaya geçtiğinde geldiği zamanı bulur.
            break

    pairs = []
    for i in range(0, len(values), 4):
        if values[i + 3] == test_id:
            new_list = []
            new_list.append(float(values[i]) - float(padding))
            new_list.append(float(values[i + 1]))
            new_list.append(float(values[i + 2]) - float(first_time))

            pairs.append(new_list)

    #fixation_pairs = ivt(pairs, 50)  # IVT algorithm for generating the fixation points
    fixation_pairs = idt(pairs,20,100)  # IVT algorithm for generating the fixation points

    id_counter = 1

    data_eye_track = []  # creating empty array

    # web-page id for each page
    media_id_dictionary = {-1: "None",
                           0: "Apple",
                           1: "AVG",
                           2: "Babylon",
                           3: "BBC",
                           4: "GoDaddy",
                           5: "Yahoo"}

    for fixation in fixation_pairs:
        # calling the finding element, sending the coordinates(X, Y) , azalmaOrani, and web-page id for finding the screen element
        element = screen_find_element((fixation[0], fixation[1]), azalma_orani, media_id_dictionary[test_id])

        # creating a new row = ["ID", "X", "Y", "First Time", "Duration","Total Fixation Count", "Element"]
        row = [id_counter, fixation[0], fixation[1], fixation[2], fixation[3], fixation[4], element]

        data_eye_track.append(row)  # appending the row to my array
        id_counter += 1  # incrementing the id counter
    computed_metrics_dictionary = compute_metrics(data_eye_track, media_id_dictionary[
        test_id])  # main part of computing the metrices (features dictionary returned)

    csv_file_computed = f'{user_id}_metrics.csv' # .csv name
    header = "Time to 1st View (sec),Revisits (#),Fixations (#),Time Viewed,Patient ID\n"  # header for my .csv

    # Print header to the file
    if test_id == 0:  # first page
        with open(csv_file_computed, 'w') as f:  # creating (if not exists) and writing to .csv file
            f.write(header)  # with header that we already defined

    data = {  # all my data for my .csv
        "Media ID": [],
        "Media Name": [],
        "User ID": [],
        "User Name": [],
        "User Gender": [],
        "AOI": [],
        "Fixation Duration": [],
        "Time To First": [],
        "Time Viewed": [],
        "Fixations (#)": [],
        "Revisits": []
    }

    total_time = 0.0

    for element_key in computed_metrics_dictionary.keys():
        duration = computed_metrics_dictionary[element_key][0]  # first index duration
        total_time = total_time + duration  # updating the total time with duration

    for element_key in computed_metrics_dictionary.keys():
        duration = round(computed_metrics_dictionary[element_key][0], 3)  # rounding with 3 digits
        first_time = round(computed_metrics_dictionary[element_key][1], 3)  # rounding with 3 digits (first-time look)
        revisits = computed_metrics_dictionary[element_key][2]  # revisit
        total_fixation = computed_metrics_dictionary[element_key][3]  # total_fixation

        # appending the data
        data["AOI"].append(str(test_id + 1) + str(element_key))
        data["Fixation Duration"].append(duration)
        data["Time To First"].append(first_time)
        data["Revisits"].append(revisits)
        data["Media ID"].append(test_id)
        data["Media Name"].append(media_id_dictionary[test_id])
        data["User ID"].append(user_id)
        data["User Name"].append(
            "Test User")  # these patient name and gende are not needed also for AI, later we will delete it from data and .csv
        data["User Gender"].append("F")

        try:
            time_viewed = round((duration / total_time) * 100, 3)  # finding the time viewed with percentage
        except ZeroDivisionError:
            time_viewed = 0

        data["Time Viewed"].append(time_viewed)
        data["Fixations (#)"].append(total_fixation)


    df = pd.DataFrame(  # benefit from pandas
        {"Time to 1st View (sec)": data["Time To First"], "Revisits (#)": data["Revisits"], "Fixations (#)": data["Fixations (#)"],
         "Time Viewed": data["Time Viewed"], "Patient ID": data["User ID"]}
    )


    df.to_csv(csv_file_computed, mode='a', header=False,index=False)  # mode : append, header False because we already defined it, index:false bcs we dont need a seperate index column


    if test_id == 1:
        current_patient = user_id


        file_path = csv_file_computed  # CSV dosyasının dosya yolu
        data = pd.read_csv(file_path)

        current_patient = int(current_patient)

        # current_patient ID'si ile eşleşen satırları bulma
        filtered_data = data[data['Patient ID'] == current_patient]

        data_to_send = {}

        time_first = filtered_data['Time to 1st View (sec)'].tolist()
        revisit = filtered_data['Revisits (#)'].tolist()
        fixation = filtered_data['Fixations (#)'].tolist()
        time_view = filtered_data['Time Viewed'].tolist()

        data_to_send["Time to 1st View (sec)"] = time_first
        data_to_send["Revisits (#)"] = revisit
        data_to_send["Fixations (#)"] = fixation
        data_to_send["Time Viewed (sec)"] = time_view


        response_data = insert_user_data(data_to_send)

        if response_data == "Non-ASD":
            result = 0
        else:
            result = 1

        # patients = Patients.query.filter_by(doctors_id=current_user.id).all()
        #
        # for patient in patients:
        #     if patient.id == current_patient:
        #         target_patient = patient
        #         break
        #
        # target_patient.result = result

        test = Test.query.filter_by(id=user_id).all()[0]
        test.result = result

        # Commit the changes to the database
        db.session.commit()
        os.remove(csv_file_computed)


    return jsonify({'message': 'File sent successfully'})  # returning confirmation message

@app.route('/accuracy_save')
@login_required
def accuracy_save():
    accuracy = int(request.args.get('input', None))
    current_test = int(request.args.get('id'))

    test = Test.query.filter_by(id=current_test).all()[0]
    test.Accuracy = accuracy

    # Commit the changes to the database
    db.session.commit()

    return "Data Successfully sent"

@app.route('/done')
@login_required
def done_endpoint():
    return render_template('done.html')


@app.post("/search")
@login_required
def search_items():
    searched_patients = []
    tests = {}
    keywords = request.json.get('keywords')
    if keywords:
        pattern = keywords.lower()

        all_patients = Patients.query.filter_by(doctors_id=current_user.id).all()

        for patient in all_patients:
            date_string = str(patient.date).split(' ')[0]
            # Convert the string to a datetime object
            date_object = datetime.strptime(date_string, "%Y-%m-%d")

            # Format the date in the desired way
            formatted_date = date_object.strftime("%d.%m.%Y")
            if (re.search(pattern, patient.name.lower()) or re.search(pattern, formatted_date)
                    or re.search(pattern, patient.surname.lower()) or re.search(pattern, patient.phonenum)
            ):
                searched_patients.append(patient)
        for patient in searched_patients:
            test = Test.query.filter_by(patient_id=patient.id).all()[0]
            tests[patient.name] = test
        form=PatientForm()
        if form.validate_on_submit():
            patient = Patients(name=form.Name.data, surname=form.Surname.data,
                               phonenum=form.Tel.data, doctors_id=current_user.id)
            db.session.add(patient)
            db.session.commit()
            test = Test(patient_id=patient.id)
            db.session.add(test)
            db.session.commit()
            flash(f"Your patient is created!", "success")
            return redirect(url_for("dashboard"))
        return render_template('dashboard.html', title='Dashboard', patients=searched_patients, form=form,tests=tests)
    else:
        return redirect(url_for("dashboard"))




@app.route('/create_new_test/<string:patient_id>')
@login_required
def create_new_test(patient_id):
    for_patient = Patients.query.filter_by(doctors_id=current_user.id,id=patient_id).one()
    new_test = Test(patient_id=patient_id)
    db.session.add(new_test)
    db.session.commit()
    for_patient.test_id = new_test.id
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route('/delete/<string:patient_id>')
@login_required
def delete(patient_id):
    patient = Patients.query.filter_by(doctors_id=current_user.id,id=patient_id).one()

    tests = Test.query.filter_by(taker=patient).all()
    for test in tests:
        db.session.delete(test)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route('/patient_history/<string:patient_id>')
@login_required
def patient_history(patient_id):
    patient = Patients.query.filter_by(doctors_id=current_user.id,id=patient_id).one()
    tests = Test.query.filter_by(taker=patient).order_by(desc(Test.date)).all()
    return render_template('patient_history.html', title='History',quantity=len(tests), patient=patient,tests=tests)

@app.route('/update_doctors_hospital_name')
@login_required
def update_doctors_hospital_name():
    new_hospital_name = request.form.get('new_input_hospital_name')
    return 'New hospital name received: {}'.format(new_hospital_name)


@app.route('/update_name', methods=['POST'])
@login_required
def update_name():
    doctor = Doctor.query.filter_by(id=current_user.id).one()
    new_name = request.json.get('name')
    if new_name:
        if doctor.name != new_name:
            doctor.name=new_name
            db.session.commit()
        return jsonify({'message': 'Name updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400


@app.route('/update_surname', methods=['POST'])
@login_required
def update_surname():
    doctor = Doctor.query.filter_by(id=current_user.id).one()
    new_name = request.json.get('name')
    if new_name:
        if doctor.surname != new_name:
            doctor.surname=new_name
            db.session.commit()
        return jsonify({'message': 'Name updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400

@app.route('/update_username', methods=['POST'])
@login_required
def update_username():
    doctor = Doctor.query.filter_by(id=current_user.id).one()
    new_name = request.json.get('name')
    if new_name:
        if doctor.username != new_name:
            doctor.username=new_name
            db.session.commit()
        return jsonify({'message': 'Name updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400

@app.route('/update_email', methods=['POST'])
@login_required
def update_email():
    doctor = Doctor.query.filter_by(id=current_user.id).one()
    new_name = request.json.get('name')
    if new_name:
        if doctor.email != new_name:
            doctor.email=new_name
            db.session.commit()
        return jsonify({'message': 'Name updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400

@app.route('/update_p_num', methods=['POST'])
@login_required
def update_p_num():
    doctor = Doctor.query.filter_by(id=current_user.id).one()
    new_name = request.json.get('name')
    if new_name:
        if doctor.phonenum != new_name:
            doctor.phonenum=new_name
            db.session.commit()
        return jsonify({'message': 'Name updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400

@app.route('/update_adress', methods=['POST'])
@login_required
def update_adress():
    doctor = Doctor.query.filter_by(id=current_user.id).one()
    new_name = request.json.get('name')
    if new_name:
        if doctor.adress != new_name:
            doctor.adress=new_name
            db.session.commit()
        return jsonify({'message': 'Name updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400

@app.route('/update_hospital_name', methods=['POST'])
@login_required
def update_hospital_name():
    doctor = Doctor.query.filter_by(id=current_user.id).one()
    new_name = request.json.get('name')
    if new_name:
        if doctor.hospital_name != new_name:
            doctor.hospital_name=new_name
            db.session.commit()
        return jsonify({'message': 'Name updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400



@app.route('/grid_data', methods=['GET','POST'])
@login_required
def grid_data():
    # Access the data sent in the request's body
    data = request.get_json()  # get the json data from the post request

    eye_tracking_data = data['eyeTrackingData']  # eye tracking data x, y, clock
    azalma_orani = data['azalmaOrani']  # azalmaOrani value
    padding = data['widthRatio']  # padding value
    test_id = data['testID']  # testID for each page
    user_id = data['id']  # unique user id for each patient generated and fetched

    values = []  # empty values array created for each /save_data endpoint called (each 'Next Button' clicked)

    for data_point in eye_tracking_data:
        values.extend(data_point)  # extending the values array for all gaze points

    # for adjusting the clock part

    first_time = 0
    for i in range(0, len(values), 4):
        if values[i + 3] == test_id:
            first_time = values[i + 2]  # her yeni sayfaya geçtiğinde geldiği zamanı bulur.
            break

    pairs = []
    for i in range(0, len(values), 4):
        if values[i + 3] == test_id:
            new_list = []
            new_list.append(float(values[i]) - float(padding))
            new_list.append(float(values[i + 1]))
            new_list.append(float(values[i + 2]) - float(first_time))

            pairs.append(new_list)

    # fixation_pairs = ivt(pairs, 50)  # ivt algorithm for generating the fixation points
    fixation_pairs = idt(pairs, 20, 100)  # idt algorithm for generating the fixation points

    id_counter = 1

    data_eye_track = []  # creating empty array

    # web-page id for each page
    media_id_dictionary = {-1: "None",
                           0: "Apple",
                           1: "AVG",
                           2: "Babylon",
                           3: "BBC",
                           4: "GoDaddy",
                           5: "Yahoo"}

    for fixation in fixation_pairs:
        # calling the finding element, sending the coordinates(X, Y) , azalmaOrani, and web-page id for finding the screen element
        # for first modal : screen_find_element
        element = grid_find_element((fixation[0], fixation[1]), azalma_orani)

        # creating a new row = ["ID", "X", "Y", "First Time", "Duration","Total Fixation Count", "Element"]
        row = [id_counter, element, test_id, fixation[2]]

        data_eye_track.append(row)  # appending the row to my array
        id_counter += 1  # incrementing the id counter


    csv_file_computed = f'{user_id}_grid_metrics.csv'  # .csv name
    header = "Fixation ID,APPLE,BABYLON,AVG,GODADDY,BBC,A,B,C,D,E,F,G,H,I,Relevant,Central,Time,Class,Patient ID\n"  # header for my .csv

    # Print header to the file
    if test_id == 0:  # first page
        with open(csv_file_computed, 'w') as f:  # creating (if not exists) and writing to .csv file
            f.write(header)  # with header that we already defined
    data = {  # all my data for my .csv
        "Fixation ID": [],
        "apple": [],
        "babylon": [],
        "avg": [],
        "godaddy": [],
        "bbc": [],
        "A": [],
        "B": [],
        "C": [],
        "D": [],
        "E": [],
        "F": [],
        "G": [],
        "H": [],
        "I": [],
        "relevant": [],
        "central": [],
        "time": [],
        "class": [],
        "User ID": []
    }
    words = ["A","B","C","D","E","F","G","H","I"]

    key_mapping = {
        0: "apple",
        1: "babylon",
        2: "avg",
        3: "godaddy",
        4: "bbc"
    }

    for grid_data in data_eye_track:
        data["Fixation ID"].append(grid_data[0])
        # time added here
        data["time"].append(grid_data[3])
        for i in range(5):
            data[key_mapping[i]].append(1 if grid_data[2] == i else 0)

        data_total = [1 if word == grid_data[1] else 0 for word in words]
        for i, word in enumerate(words):
            data[word].append(data_total[i])
        data["relevant"].append(0)
        data["central"].append(0)
        data["class"].append(0)
        data["User ID"].append(user_id)


    df = pd.DataFrame(  # benefit from pandas
        {"Fixation ID": data["Fixation ID"], "APPLE": data["apple"], "BABYLON": data["babylon"], "AVG": data["avg"],
         "GODADDY": data["godaddy"], "BBC": data["bbc"],
         "A": data["A"], "B": data["B"], "C": data["C"], "D": data["D"], "E": data["E"], "F": data["F"], "G": data["G"],
         "H": data["H"], "I": data["I"], "Relevant": data["relevant"], "Central": data["central"], "Time": data["time"], "Class": data["class"], "Patient ID": data["User ID"]}
    )


    df.to_csv(csv_file_computed, mode='a', header=False,index=False)  # mode : append, header False because we already defined it, index:false bcs we dont need a seperate index column

    if test_id == 4:
        current_patient = user_id


        file_path = csv_file_computed  # CSV dosyasının dosya yolu
        data = pd.read_csv(file_path)

        current_patient = int(current_patient)

        # current_patient ID'si ile eşleşen satırları bulma
        filtered_data = data[data['Patient ID'] == current_patient]

        data_to_send = {}

        time = filtered_data['Time'].tolist()
        a = filtered_data['A'].tolist()
        b = filtered_data['B'].tolist()
        d = filtered_data['D'].tolist()
        e = filtered_data['E'].tolist()
        apple = filtered_data['APPLE'].tolist()
        babylon = filtered_data['BABYLON'].tolist()
        avg = filtered_data['AVG'].tolist()
        godaddy = filtered_data['GODADDY'].tolist()
        bbc = filtered_data['BBC'].tolist()

        data_list = []
        for i in range(len(time)):
            data_list.append([time[i],a[i], b[i], d[i], e[i], apple[i], babylon[i], avg[i], bbc[i], godaddy[i]])

        response_data = insert_user_data2(data_list)

        if response_data == "Non-ASD":
            result = 0
        else:
            result = 1

        test = Test.query.filter_by(id=user_id).all()[0]
        test.Second_Result = result

        db.session.commit()
        os.remove(csv_file_computed)


    return jsonify({'message': 'File sent successfully'})  # returning confirmation message



@app.route('/validateDoctor/<string:doctor_id>', methods=['POST','GET'])
@login_required
def validateDoctor(doctor_id):
    doctor = Doctor.query.filter_by(id=doctor_id).one()
    doctor.IsValidated = 1
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route('/UnvalidateDoctor/<string:doctor_id>', methods=['POST','GET'])
@login_required
def UnvalidateDoctor(doctor_id):
    doctor = Doctor.query.filter_by(id=doctor_id).one()
    doctor.IsValidated = 0
    db.session.commit()
    return redirect(url_for("dashboard"))

