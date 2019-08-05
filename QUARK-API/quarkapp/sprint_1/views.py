from django.shortcuts import render
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from bson import json_util
from dbconfig.db import getConnection
from django.core.mail import send_mail
from sprint_2.cryptography import encryption,decryption
import bcrypt


# Create your views here.

# Sign up API
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        # print(request.body)
        reqData = request.body.decode('utf8')
        print(reqData)
        data = json.loads(reqData)

        # User input during signup
        data={
            "first_name":data['first_name'],
            "last_name": data['last_name'],
            "username":data['username'],
            "password": bcrypt.hashpw(data['password'].encode('utf8'), bcrypt.gensalt(14)).decode('utf-8'),
            # "password":data['password'],
            "roles":data['roles'],
            "status":"inactive"
        }

        print(data)

        # mongoDB connection establishment
        conn=getConnection()
        collection=conn['users']

        # Find if the User is Already Exists
        getData=collection.find({'username': data['username']})
        if (list(getData)):
            return JsonResponse({
                "reason": "User Already Exists",
                "message":"Failure"
            })

        # If the user is not exist, store to database.
        collection.insert_one(data)
        fullname = "{} {}".format(data['first_name'], data['last_name'])
        encUsername = encryption(data['username'])

        # Call send_email function to send email confirmation and account activation..
        subject = "Email Verification and Activation."
        message = """
        Dear {1},

        Please click on the below link for email verification and account activation:

        https://quarkapp.herokuapp.com/verify?username={0}

        Yours Truly,
        QUARK Support Team
        """.format(encUsername, fullname)

        # Send Email during user sign up.
        # send_email(data['username'], subject, message)
        test_email(data['username'], subject, message)

        # dumps: convert json to json string
        data=json.dumps(data,default=json_util.default)

        # loads: convert json string to json
        data=json.loads(data)
        return JsonResponse({
            "message":"Success",
            "data": data
        })
    return JsonResponse({
        "reason":"Requested method not allowed " + request.method,
        "message":"Failure"
    })


#  Makes the user active when the user clicks on the link sent to their email for login.
def verify_user(request):
    username=request.GET['username']

    decryptUsername = decryption(username)
    # mongoDB connection establishment
    conn = getConnection()
    collection = conn['users']

    # Defining where and set condition for update
    cond = {
        "username": decryptUsername
    }
    data = {
        "$set": {"status": "active"}
    }
    try:
        if collection.update(cond, data):
            return render(request,'verify_email.html')
    except TypeError as e:
        print(e)
    except ValueError as e:
        print(e)


# Login API
@csrf_exempt
def login(request):
    if request.method == 'POST':
        reqData = request.body.decode('utf8')
        data = json.loads(reqData)

        # User input from FE during login.
        username = data['username']
        password = data['password']

        # mongoDB connection establishment
        conn = getConnection()
        collection = conn['users']

        docs_list = list(collection.find({'username': username}))
        data = json.dumps(docs_list, default=json_util.default)
        data = json.loads(data)
        
        # Check user exists or not.
        if data:
            if bcrypt.checkpw(password.encode('utf8'), data[0]['password'].encode('utf8')):
                    # docs_list = list(collection.find({'username': username, 'password': password}))
                    # data = json.dumps(docs_list, default=json_util.default)
                    # data = json.loads(data)
                statusdata = data[0]
                statusdata = statusdata["status"]
                if statusdata == "active":
                    return JsonResponse({
                    "reason": "User is active",
                    "message": "Success",
                    "data" :data
                })
                else:
                    return JsonResponse({
                    "reason": "ACTIVATE your account by clicking on the verification URL sent to your email ID.",
                    "message": "Failure"
                    })
            # except ValueError as ve:
            return JsonResponse({
            "reason": "Incorrect Credentials",
            "message": "Failure"
            })
                # else:
                #     print(False)
                #     # return JsonResponse({
                #     #     "reason": "Incorrect Credentials",
                #     #     "message": "Failure"
                #     # })
        else:
            return JsonResponse({
                "reason": "User Does Not Exist",
                "message": "Failure"
            })


# Validate User API during forgot password
@csrf_exempt
def validate_email(request):
    if request.method == 'POST':
        reqData = request.body.decode('utf8')
        data = json.loads(reqData)
        username = data['username']

        # mongoDB connection establishment
        conn = getConnection()
        collection = conn['users']

        # Check whether user email exists or not
        docs_list = list(collection.find({'username': username}))

        data = json.dumps(docs_list, default=json_util.default)
        data = json.loads(data)
        if data:
            data = data[0]
            fullname = "{} {}".format(data["first_name"], data["last_name"])

            # Call send_email function to send email for password reset.
            subject = "Password Reset Link"
            message = """
            Dear {1},

            Please click on the below link to reset your password:

            https://quark-app.herokuapp.com/q_pawrd?username={0}

            Yours Truly,
            QUARK Support Team
            """.format(username, fullname)

            # Send email during forgot password
            # send_email(username , subject , message)
            test_email(username , subject , message)

            return JsonResponse({
                "message": "Success",
                "data": data
            })
        else:
            return JsonResponse({
                "reason": "Email not Found.",
                "message": "Failure"
            })

# Password Rest API
@csrf_exempt
def update_password(request):
    if request.method == 'POST':
        reqData = request.body.decode('utf8')
        data = json.loads(reqData)
        
        # User input during update password
        username = data['username']
        password = data['password']

        # mongoDB connection establishment
        conn = getConnection()
        collection = conn['users']

        docs_list = list(collection.find({'username': username},{'password': 1,'_id':0}))
        data = json.dumps(docs_list, default=json_util.default)
        data = json.loads(data)

        # if dbData[0]['password']!=password:

        #     # Defining where and set condition for update
        #     cond={
        #         "username" : username
        #     }
        #     data={
        #         "$set": {"password":password}
        #     }
        #     # Update collection
        #     if collection.update(cond,data):
        #         return JsonResponse({
        #             "message": "Success",
        #             "data": data
        #         })
        # else:
        #     return JsonResponse({
        #         "message": "Failure",
        #         "reason": "Your Password is same as Old Password.\nPlease choose a new one"
        #     })

        if bcrypt.checkpw(password.encode('utf8'), data[0]['password'].encode('utf8')):
            return JsonResponse({
                "message": "Failure",
                "reason": "Your Password is same as Old Password.\nPlease choose a new one"
            })
        else:
            cond = {
                "username":username
            }
            data = {
                "$set": {"password": bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(14)).decode('utf-8')}
            }

            # Update collection
            if collection.update(cond,data):
                return JsonResponse({
                    "message": "Success",
                    "data": data
                })




# Send Email
# def send_email(username , subject , message):
#     pythoncom.CoInitialize()
#     outlook = win32com.client.Dispatch("Outlook.Application")
#     olMailItem = 0
#     newMail = outlook.CreateItem(olMailItem)
#     newMail.Subject = subject
#     newMail.Body = message
#     newMail.To = username
#     newMail.SentOnBehalfOfName = 'quarksupport@eainfobiz.com'
#     if newMail.Send():
#         return JsonResponse({
#             "message": "Success",
#             "Receiver": username
#         })
#     else:
#         return JsonResponse({
#             "message": "Failure"
#         })


# Test Email
def test_email(username , subject , message):
    if send_mail(
        subject,
        message,
        'quarksupport@eainfobiz.com',
        [username],
        fail_silently=False,
    ):
        return JsonResponse({
            "message" : "Success",
        })
