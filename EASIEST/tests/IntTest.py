# Python code to find the fields using ID
# Submit button will be tracked using the CSS Selector
import time

from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from EASIEST import app, db
from EASIEST.database import Doctor, Patients, Test, Admin, User
from flask_login import current_user

# Initialize a web driver (you may need to download and specify the driver for your browser)
def Registration_test():
    driver = webdriver.Chrome()
    try:
        # Open the webpage with the form
        driver.get("http://127.0.0.1:5000/register")

        # Fill in the form fields
        driver.find_element(by=By.ID, value="Name").send_keys("Kaya")
        driver.find_element(by=By.ID, value="Surname").send_keys("Daniilovna")
        driver.find_element(by=By.ID, value="Username").send_keys("KayaTheBest")
        driver.find_element(by=By.ID, value="Email").send_keys("kaya@gmail.com")
        driver.find_element(by=By.ID, value="Tel").send_keys("12341234")
        driver.find_element(by=By.ID, value="Address").send_keys("odtu")
        driver.find_element(by=By.ID, value="Hospital").send_keys("odtu_hos")
        driver.find_element(by=By.ID, value="Password").send_keys("1234")
        driver.find_element(by=By.ID, value="Confirm_password").send_keys("1234")

        # Submit the form
        driver.find_element(by=By.ID, value="Submit").submit()
        with app.app_context():
            user = User.query.filter_by(email='kaya@gmail.com').first()
            if user:
                print('\nRegistration Test Passed\n')
    except Exception as e:
        print(e)
    # Close the browser
    driver.quit()

def Login_Doctor_Test_Not_Valid():
    driver = webdriver.Chrome()
    try:
        # Open the webpage with the form
        driver.get("http://127.0.0.1:5000/login")

        # Fill in the form fields
        driver.find_element(by=By.ID, value="Email").send_keys("kaya@gmail.com")
        driver.find_element(by=By.ID, value="Password").send_keys("1234")

        # Submit the form
        driver.find_element(by=By.ID, value="Submit").submit()
        try:
            value = driver.find_element(by=By.ID, value="doctor_status")
            if value.text == 'Your Personal information has not yet been validated':
                print('\nNot Validated Test Passed\n')
        except Exception as er:
            print(er)
    except Exception as e:
        print(e)
    # Close the browser
    driver.quit()

def Login_Admin_Test():
    id = 0
    with app.app_context():
        user = User.query.filter_by(email='kaya@gmail.com').first()
        id= user.id
    driver = webdriver.Chrome()
    try:
        # Open the webpage with the form
        driver.get("http://127.0.0.1:5000/login")

        # Fill in the form fields
        driver.find_element(by=By.ID, value="Email").send_keys("admin@gmail.com")
        driver.find_element(by=By.ID, value="Password").send_keys("1234")

        # Submit the form
        driver.find_element(by=By.ID, value="Submit").submit()
        driver.get("http://127.0.0.1:5000/validateDoctor/"+str(id))
        with app.app_context():
            user = Doctor.query.filter_by(id=str(id)).first()
            if user.IsValidated:
                print('\nAdmin Test Passed\n')
    except Exception as e:
        print(e)
    # Close the browser
    print(current_user)
    driver.quit()



def Login_Valid_Doctor_Test():
    id = 0
    with app.app_context():
        user = User.query.filter_by(email='kaya@gmail.com').first()
        id = user.id
    driver = webdriver.Chrome()
    try:
        # Open the webpage with the form
        driver.get("http://127.0.0.1:5000/login")

        # Fill in the form fields
        driver.find_element(by=By.ID, value="Email").send_keys("kaya@gmail.com")
        driver.find_element(by=By.ID, value="Password").send_keys("1234")

        # Submit the form
        driver.find_element(by=By.ID, value="Submit").submit()
        try:
            value = driver.find_element(by=By.ID, value="doctor_valid_status")
            if value.text == 'Patients List':
                print('\nPatient List Test Passed\n')
        except Exception as er:
            print(er)

        driver.find_element(by=By.ID, value="myBtn").click()
        driver.find_element(by=By.ID, value="Name").send_keys("Optimus")
        driver.find_element(by=By.ID, value="Surname").send_keys("Prime")
        driver.find_element(by=By.ID, value="Tel").send_keys("12322175")
        driver.find_element(by=By.ID, value="Submit").submit()
        with app.app_context():
            user = Patients.query.filter_by(doctors_id=str(id)).first()
            if user:
                print('\nAdd patient Test Passed\n')

    except Exception as e:
        print(e)
    # Close the browser
    driver.quit()


def Hospital_Update_Test():
    id = 0
    with app.app_context():
        user = User.query.filter_by(email='kaya@gmail.com').first()
        id = user.id
    driver = webdriver.Chrome()
    try:
        # Open the webpage with the form
        driver.get("http://127.0.0.1:5000/login")

        # Fill in the form fields
        driver.find_element(by=By.ID, value="Email").send_keys("kaya@gmail.com")
        driver.find_element(by=By.ID, value="Password").send_keys("1234")

        # Submit the form
        driver.find_element(by=By.ID, value="Submit").submit()

        driver.get("http://127.0.0.1:5000/account")

        driver.find_element(by=By.ID, value="adress_update").click()
        driver.find_element(by=By.ID, value="new_adress").send_keys("Moscow")
        driver.find_element(by=By.ID, value="Upadet_button_adress").click()

        with app.app_context():
            user = Doctor.query.filter_by(id = str(id)).first()
            if user.adress =='Moscow':
                print('\nUpdate Test Passed\n')

    except Exception as e:
        print(e)
    # Close the browser
    driver.quit()


if __name__=='__main__':
    cycle=True
    while(cycle):
        choice = input("Choose test\n"
              "1) Registration\n"
              "2) Login Anvalidated Doctor\n"
              "3) Login Admin\n"
              "4) Login Validated Doctor\n"
              "5) Update Address\n"
              "Your input: ")

        if choice == '1':
            Registration_test()
        elif choice == '2':
            Login_Doctor_Test_Not_Valid()
        elif choice == '3':
            Login_Admin_Test()
        elif choice == '4':
            Login_Valid_Doctor_Test()
        elif choice == '5':
            Hospital_Update_Test()
        else:
            print('Wrong input\n')
