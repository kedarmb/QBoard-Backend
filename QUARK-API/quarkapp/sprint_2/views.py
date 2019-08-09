from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from bson import json_util
from dbconfig.db import getConnection
import plotly
import plotly.graph_objs as go
import xlrd
import datetime
import bcrypt

# Create your views here.

# Profile Update API
@csrf_exempt
def profile_update(request):
    if request.method == 'POST':
        reqData = request.body.decode('utf8')
        reqData = json.loads(reqData)
        username = reqData['username']
        firstName=reqData['first_name']
        lastName=reqData['last_name']

        conn = getConnection()
        collection = conn['users']

        docs_list = list(collection.find({"username" : username}))
        data = json.dumps(docs_list, default=json_util.default)
        data = json.loads(data)
        if data:
            if firstName is not None and lastName == "":
                cond = {
                    "username": username
                }
                data = {
                    "$set": {"first_name": reqData['first_name']}
                }
                if collection.update(cond, data):
                    return JsonResponse({
                        "reason": "Your Profile updated successfully.",
                        "message": "Success",
                        "data": data
                    })
            elif lastName is not None and firstName == "":
                cond = {
                    "username": username
                }
                data = {
                    "$set": {"last_name": reqData['last_name']}
                }
                if collection.update(cond, data):
                    return JsonResponse({
                        "reason": "Your Profile updated successfully.",
                        "message": "Success",
                        "data": data
                    })
            elif firstName is not None and lastName is not None:
                cond = {
                    "username": username
                }
                data = {
                    "$set": {"first_name": reqData['first_name'], "last_name": reqData['last_name']}
                  }
                if collection.update(cond, data):
                    return JsonResponse({
                        "reason": "Your Profile updated successfully.",
                        "message": "Success",
                        "data": data
                    })

                else:
                    return JsonResponse({
                        "message": "Failure",
                    })

        else:
            return JsonResponse({
                "reason" : "User email does not exist.",
                "message" : "Failure"
            })

# # Reset Password API
# @csrf_exempt
# def reset_password(request):

#     # get data from request body
#     reqData = request.body.decode('utf8')
#     data = json.loads(reqData)
#     username = data['username']
#     oldPassword = data['oldpassword']
#     newPassword = data['newpassword']
#     if oldPassword != newPassword:

#         # mongoDB connection establishment
#         conn = getConnection()
#         collection = conn['users']

#         # check old password
#         docs_list = list(collection.find({'username': username, 'password': oldPassword}))
#         docs_list = list(collection.find({'username': username}))
#         data = json.dumps(docs_list, default=json_util.default)
#         data = json.loads(data)

#         if data:

#             print(data[0]['password'])
#             # if bcrypt.checkpw(oldPassword.encode('utf8'), data[0]['password'].encode('utf8')):

#             # Defining where and set condition for update
#             cond = {
#                 "username": username
#             }
#             data = {
#                 "$set": {"password": bcrypt.hashpw(newPassword.encode('utf8'), bcrypt.gensalt(14)).decode('utf-8')}
#             }
#             # Update collection
#             if collection.update(cond, data):
#                 return JsonResponse({
#                     "message": "Success",
#                     "username": username
#                 })
#             else:
#                 return JsonResponse({
#                     "message": "Failure",
#                     "reason": "Password does not match"
#                 })
#         else:
#             return JsonResponse({
#                 "message": "Failure",
#                 "reason": "Current password is wrong"
#             })
#     else:
#         return JsonResponse({
#             "message": "Failure",
#             "reason": "Current password and New Password Should be Different"
#         })

#Reset Password API
@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        reqData = request.body.decode('utf8')
        data = json.loads(reqData)

        username = data['username']
        oldPassword = data['oldpassword']
        newPassword = data['newpassword']

        # mongoDB connection establishment
        conn = getConnection()
        collection = conn['users']

        docs_list = list(collection.find({'username': username}))
        data = json.dumps(docs_list, default=json_util.default)
        data = json.loads(data)

        if data:
            if bcrypt.checkpw(oldPassword.encode('utf8'), data[0]['password'].encode('utf8')):
                if oldPassword != newPassword:
                    cond = {
                        "username": username
                        }
                    data = {
                        "$set": {"password": bcrypt.hashpw(newPassword.encode('utf8'), bcrypt.gensalt(14)).decode('utf-8')}
                        }
                    # Update collection
                    if collection.update(cond, data):
                        return JsonResponse({
                            "message": "Success",
                            "username": username
                            })
                else:
                    return JsonResponse({
                        "message": "Failure",
                        "reason": "Current password and New Password Should be Different"
                    })
            else:
                return JsonResponse({
                    "message": "Failure",
                    "reason": "Current password is wrong"
                })


# Read Excel File and insert data into MongoDB
@csrf_exempt
def read_file(request):
    wb = xlrd.open_workbook('TestData.xlsx')
    sh = wb.sheet_by_index(0)

    # List to hold dictionaries
    r = list(sh.row(0))  # returns all the CELLS of row 0,
    columan_name = []  # make a data store
    columan_name.append(sh.row_values(0))
    data_list = []
    data={}
    conn = getConnection()
    collection = conn['testExcelData']

    # Iterate through each row in worksheet and fetch values into dict
    for rownum in range(1, sh.nrows):
        row_values = sh.row_values(rownum)
        for i in range(0,len(columan_name[0])):
            data[columan_name[0][i]]=row_values[i]
        data_list.append(data.copy())
    collection.insert_many(data_list.copy())

    return JsonResponse({
        "message": "success",
    })

#read test data from mongo and sent to FE
@csrf_exempt
def excel_data(request):
    conn = getConnection()
    collection = conn['excelData']
    module_list = list(collection.distinct("Module"))
    final=[]
    for i in module_list:
        dataList =list(collection.find({'Actual Result': 'Fail', 'Module':i}, {"_id": 0}))
        data = json.dumps(dataList, default=json_util.default)
        data = json.loads(data)
        final.append(data)
    data=dict(zip(module_list,final))
    return JsonResponse({
        "message": "success",
        "data":final
    })


# Read data from MongoDB and plot the graph
def plot_graph(request):
    Execution_Date = ['02-03-2019', '03-03-2019', '07-03-2019', '10-03-2019']

    Absence_Management = [2, 0, 1, 3]
    Benefits = [1, 1, 2]
    Core_HR = [2, 4, 1, 2]
    LMS = [8, 5, 4, 32]
    Payroll = [0, 1, 1, 2]
    Talent_Management = [6, 3, 4, 6]

    # Create and style traces
    trace0 = go.Scatter(
        x=Execution_Date,
        y=Absence_Management,
        name='Absence Management',
        line=dict(
            color=('rgb(244, 149, 66)'))
    )
    trace1 = go.Scatter(
        x=Execution_Date,
        y=Benefits,
        name='Benefits',
        line=dict(
            color=('rgb(249, 0, 29)'))
    )
    trace2 = go.Scatter(
        x=Execution_Date,
        y=Core_HR,
        name='Core HR',
        line=dict(
            color=('rgb(23, 140, 39)'))
    )
    trace3 = go.Scatter(
        x=Execution_Date,
        y=LMS,
        name='LMS',
        line=dict(
            color=('rgb(71, 24, 24)'))
    )
    trace4 = go.Scatter(
        x=Execution_Date,
        y=Payroll,
        name='Payroll',
        line=dict(
            color=('rgb(54, 4, 204)'))
    )

    trace5 = go.Scatter(
        x=Execution_Date,
        y=Talent_Management,
        name='Talent Management',
        line=dict(
            color=('rgb(4, 204, 127)'))
    )
    data = [trace0, trace1, trace2, trace3, trace4, trace5]

    # Edit the layout
    layout = dict(title='DEFECT TRENDS',
                  xaxis=dict(title='Execution Date'),
                  yaxis=dict(title='Severity'),
                  )

    fig = dict(data=data, layout=layout)
    div = plotly.offline.plot(fig, output_type='div',include_plotlyjs='cdn')
    return JsonResponse({
        "message": "Success",
        "graph": div
    })

# Test Setup API for reading data from Excel
def read_test_setup(request):
    workbook = xlrd.open_workbook('Test Case Master_Core HR.xlsx')
    worksheet = workbook.sheet_by_name('HR001')

    data = []
    keys = [v.value for v in worksheet.row(0)]
    for row_number in range(worksheet.nrows):
        if row_number == 0:
            continue
        row_data = {}
        for col_number, cell in enumerate(worksheet.row(row_number)):
            if keys[col_number] == 'Test Case #' or keys[col_number] == 'Module' or keys[col_number] == 'Test Case' or \
                    keys[col_number] == 'Test Scenarios' or keys[col_number] == 'Scenario Name' or keys[
                col_number] == 'First Name' or keys[col_number] == 'Last Name' or keys[
                col_number] == 'Address Line 1' or keys[col_number] == 'Address Line 2' or keys[
                col_number] == 'Address Line 3':
                row_data[keys[col_number]] = cell.value
        data.append(row_data.copy())
        break
    return JsonResponse({
        "message" : "Success",
        "data" : data
    })

# Test Setup API for reading data from Excel
def read_test(request):
    workbook = xlrd.open_workbook('result_2.xlsx')
    worksheet = workbook.sheet_by_index(0)

    data = []
    keys = [v.value for v in worksheet.row(3)]
    # for v in worksheet.row(3):
    #     print(v.value)
    for row_number in range(3, worksheet.nrows):
        if row_number == 3:
            continue
        row_data = {}
        for col_number, cell in enumerate(worksheet.row(row_number)):
                row_data[keys[col_number]] = cell.value
        # if row_data[keys[1]] == 'Core HR':
        data.append(row_data.copy())
        # break
    return JsonResponse({
        "message": "Success",
        "count":len(data),
        "data": data
    })


# Read data from DB and Plot the Graph
def show_graph(request):
    conn = getConnection()
    collection = conn['excelData']
    docs_list = list(collection.find({"Actual Result":"Fail"}, {"Module":1,"Execution Date":1,"Severity":1,"_id":0}))
    data = json.dumps(docs_list, default=json_util.default)
    data = json.loads(data)


    Execution_Date = []
    Core_HR = []
    Payroll = []
    Absence_Management = []
    Benefits = []
    Talent_Management = []
    LMS = []

    for ed in data:
        Execution_Date.append(ed['Execution Date'])
        # Execution_Date.append(
        #     datetime.datetime.utcfromtimestamp((ed['Execution Date'] - 25569) * 86400.0).strftime('%d-%m-%Y'))


    Execution_Date = sorted(Execution_Date, key=lambda i: datetime.datetime.strptime(i, '%d-%m-%Y'))
    print(Execution_Date)


    for i in data:

        if i['Module'] == 'Core HR' or i['Module'] == 'Payroll' or i['Module'] == 'Absence Management'\
            or i['Module'] == 'Benefits' or i['Module'] == 'Talent Management' or i['Module'] == 'LMS' :

            # Core HR
            pipe = [{ '$match': {'Module': 'Core HR'}},{
                '$group': {'_id': {'Module':'$Module','Execution Date': '$Execution Date'},
                           'Severity': {'$sum': '$Severity'}}}, {'$sort':{'_id':1}}]
            docs_list=list(collection.aggregate(pipeline=pipe))
            core_hr_data = json.dumps(docs_list, default=json_util.default)
            core_hr_data = json.loads(core_hr_data)

            # Payroll
            pipe = [{'$match': {'Module': 'Payroll'}}, {
                '$group': {'_id': {'Module': '$Module', 'Execution Date': '$Execution Date'},
                           'Severity': {'$sum': '$Severity'}}}, {'$sort': {'_id': 1}}]
            docs_list = list(collection.aggregate(pipeline=pipe))
            payroll_data = json.dumps(docs_list, default=json_util.default)
            payroll_data = json.loads(payroll_data)

            # Absence Management
            pipe = [{'$match': {'Module': 'Absence Management'}}, {
                '$group': {'_id': {'Module': '$Module', 'Execution Date': '$Execution Date'},
                           'Severity': {'$sum': '$Severity'}}}, {'$sort': {'_id': 1}}]
            docs_list = list(collection.aggregate(pipeline=pipe))
            absence_management_data = json.dumps(docs_list, default=json_util.default)
            absence_management_data = json.loads(absence_management_data)

            # Benefits
            pipe = [{'$match': {'Module': 'Benefits'}}, {
                '$group': {'_id': {'Module': '$Module', 'Execution Date': '$Execution Date'},
                           'Severity': {'$sum': '$Severity'}}}, {'$sort': {'_id': 1}}]
            docs_list = list(collection.aggregate(pipeline=pipe))
            benefits_data = json.dumps(docs_list, default=json_util.default)
            benefits_data = json.loads(benefits_data)

            # Talent Management
            pipe = [{'$match': {'Module': 'Talent Management'}}, {
                '$group': {'_id': {'Module': '$Module', 'Execution Date': '$Execution Date'},
                           'Severity': {'$sum': '$Severity'}}}, {'$sort': {'_id': 1}}]
            docs_list = list(collection.aggregate(pipeline=pipe))
            talent_management_data = json.dumps(docs_list, default=json_util.default)
            talent_management_data = json.loads(talent_management_data)

            # LMS
            pipe = [{'$match': {'Module': 'LMS'}}, {
                '$group': {'_id': {'Module': '$Module', 'Execution Date': '$Execution Date'},
                           'Severity': {'$sum': '$Severity'}}}, {'$sort': {'_id': 1}}]
            docs_list = list(collection.aggregate(pipeline=pipe))
            lms_data = json.dumps(docs_list, default=json_util.default)
            lms_data = json.loads(lms_data)

            # Core HR Severity
            for core_hr in core_hr_data:
                Core_HR.append(core_hr['Severity'])

            # Payroll Severity
            for payroll in payroll_data:
                Payroll.append(payroll['Severity'])

            # Absence Management Severity
            for absence_management in absence_management_data:
                Absence_Management.append(absence_management['Severity'])

            # Benefits Severity
            for benefits in benefits_data:
                Benefits.append(benefits['Severity'])

            # Talent Management
            for talent_management in talent_management_data:
                Talent_Management.append(talent_management['Severity'])

            # LMS
            for lms in lms_data:
                LMS.append(lms['Severity'])
            break

    # Create and style traces
    trace0 = go.Scatter(
        x=Execution_Date,
        y=Absence_Management,
        name='Absence Management',
        line=dict(
            color=('rgb(244, 149, 66)'))
    )
    trace1 = go.Scatter(
        x=Execution_Date,
        y=Benefits,
        name='Benefits',
        line=dict(
            color=('rgb(226, 9, 9)'))
    )
    trace2 = go.Scatter(
        x=Execution_Date,
        y=Core_HR,
        name='Core HR',
        line=dict(
            color=('rgb(23, 140, 39)'))
    )
    trace3 = go.Scatter(
        x=Execution_Date,
        y=LMS,
        name='LMS',
        line=dict(
            color=('rgb(71, 24, 24)'))
    )
    trace4 = go.Scatter(
        x=Execution_Date,
        y=Payroll,
        name='Payroll',
        line=dict(
            color=('rgb(54, 4, 204)'))
    )

    trace5 = go.Scatter(
        x=Execution_Date,
        y=Talent_Management,
        name='Talent Management',
        line=dict(
            color=('rgb(4, 204, 127)'))
    )
    data = [trace0, trace1, trace2, trace3, trace4, trace5]

    # Edit the layout
    layout = dict(title='DEFECT TRENDS',
                  xaxis=dict(title='Execution Date'),
                  yaxis=dict(title='Severity'),
                  )

    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig, filename="line_graph.html")
    return JsonResponse({
        "message": "Success",
        'execution_date': Execution_Date,
        'core_hr': Core_HR,
        'absence_management': Absence_Management,
        'benefits': Benefits,
        'talent_management': Talent_Management,
        'lms': LMS
    })

# API to Read RPA Output file
@csrf_exempt
def readRPAFile(request):
    wb = xlrd.open_workbook('RPA Execution Output.xlsx')
    # wb = xlrd.open_workbook('TestData.xlsx')
    # wb = xlrd.open_workbook('rpaInfo.xlsx')
    # wb = xlrd.open_workbook('result_2.xlsx')
    # wb = xlrd.open_workbook('RPA Execution Output.xlsx')
    sh = wb.sheet_by_name('Execution Details')
    # sh = wb.sheet_by_index(0)
    print(sh)
    # List to hold dictionaries
    r = list(sh.row(3))  # returns all the CELLS of row 3,
    print(r)
    column_name = []  # make a data store
    column_name.append(sh.row_values(3))
    print(column_name)
    data_list = []
    data = {}
    conn = getConnection()
    # conn.drop_collection('new_rpaInfo')
    # collection = conn['new_rpaInfo']
    collection = conn['rpaInfo']
    # collection.index_information()
    # print(len(columan_name[0]))
    # Iterate through each row in worksheet and fetch values into dict
    for rownum in range(4, sh.nrows):
        row_values = sh.row_values(rownum)
        for i in range(0, len(column_name[0])):
            # if row_values
            # if (columan_name[0][i] == 'Execution Date'):
            #     a1_as_datetime = datetime.datetime(*xlrd.xldate_as_tuple(row_values[i], wb.datemode))
            #     # print(a1_as_datetime)
            #     # data[columan_name[0][i]] = datetime.datetime.utcfromtimestamp(
            #     #     (row_values[i] - 25569) * 86400.0).strftime('%d-%m-%Y')
            #     continue
            data[column_name[0][i]] = row_values[i]
        # if data[column_name[0][1]] == 'Core HR':
        if data[column_name[0][1]]:
            # print(True)
            data_list.append(data.copy())
    # print(data_list)
    collection.insert_many(data_list)
    total_documents = collection.find().count()
    # data_list = json.dumps(data_list)
    

    return JsonResponse({
        "message": "success",
        "Total Rows" : len(data_list),
        "Total Documents": total_documents
        # "data": data_list
    })

# API for Defects by Severity
@csrf_exempt
def defects_by_severity(request):
    if request.method == 'GET':
        conn = getConnection()
        # collection = conn['rpaInfo']
        collection = conn['rpaInfo']
        module_list = list(collection.distinct("Module"))
        severity_list = list(collection.distinct("Severity"))
        severity_list = list(filter(None,severity_list))
        status_list = list(collection.distinct("Status"))
        status_list = list(filter(None, status_list))
        status_obj={}
        # module_severities =[]
        module_severities = {}

        # Modified by Kedar
        # Data for Severity Count by Module
        total_severity_count_pipe = [{'$match': {'Severity': {'$ne': ''}}}, {'$count': 'Total Severity Count'}]
        docs_total_severity_count_list = list(collection.aggregate(pipeline=total_severity_count_pipe))
        data_total_data_severity_count = json.dumps(docs_total_severity_count_list, default=json_util.default)
        data_total_data_severity_count = json.loads(data_total_data_severity_count)

        for module in module_list:
            finalData1={}

            final_obj = {}
            pipe_severity = [{'$match': {'Module': module, 'Severity': {'$ne': ''}}}, {'$count': module}]
            docs_list = list(collection.aggregate(pipeline = pipe_severity))
            data_severity = json.dumps(docs_list, default=json_util.default)
            data_severity = json.loads(data_severity)

            # Modified by Kedar
            # Object of Severity Count by Modules
            for data in data_severity:
                for keys in data.keys():
                    # final_obj['module']=keys
                    final_obj['severity_count']=data[module]
                    per = round(
                        (int(data[module])/(int(data_total_data_severity_count[0]['Total Severity Count'])))*100)
                    final_obj['severity_count_%'] = per
            module_severities[keys] = final_obj
            
            
            for status in status_list:
                finalData={}
                for severity in severity_list:
                    pipe = [{'$match': {'Module': module, 'Actual Result': 'Fail', 'Status': status,'Severity': severity}},
                            {'$count': severity}]
                    doc_list = list(collection.aggregate(pipeline = pipe))
                    dl = json.dumps(doc_list, default=json_util.default)
                    dl = json.loads(dl)

                    for data in dl:
                        finalData[severity]=data[severity]
                finalData1[status]=finalData
            status_obj[module]=finalData1

        return JsonResponse({
            "message" : "success",
            "data":status_obj,
            "result" : module_severities
        })
    else:
        return JsonResponse({
            "message" : "HTTP method not allowed"
        })

# @csrf_exempt
# def defects_by_severity(request):
#     if request.method == 'GET':
#         conn =getConnection()
#         collection = conn['RPAOutput']
#
#         module_list = list(collection.distinct("Module"))
#
#         severity_list = list(collection.distinct("Severity"))
#         severity_list = list(filter(None,severity_list))
#
#         status_list = list(collection.distinct("Status"))
#         status_list = list(filter(None, status_list))
#
#         severities =[]
#         severities_count = []
#         severity_status = []
#         severities_status = []
#
#         for module in module_list:
#             docs_list = list(collection.find({'Actual Result': 'Fail', 'Module': module}, {"_id": 0}))
#             data = json.dumps(docs_list, default=json_util.default)
#             data = json.loads(data)
#
#             for i in data:
#                 for severity in severity_list:
#                     for status in status_list:
#                         # if 'Open' in status:
#                             pipe = [{'$match': {'Module':i['Module'],'Actual Result':'Fail','Severity': severity,'Status': status}},
#                                      {'$group': {'_id': {'Status': status, 'Severity' : severity}}}]
#
#                             p = [{'$match': {'Module':i['Module'],'Actual Result':'Fail','Severity': severity,'Status': status}},
#                                  {'$count': severity}]
#
#                             doc_list = list(collection.aggregate(pipeline=pipe))
#                             dl = json.dumps(doc_list, default=json_util.default)
#                             dl = json.loads(dl)
#
#                             doc_list = list(collection.aggregate(pipeline=p))
#                             d = json.dumps(doc_list, default=json_util.default)
#                             d = json.loads(d)
#
#                             for defects in dl:
#                                 severity_status.append(defects)
#
#                             for df in d:
#                                 severities.append(df)
#                 break
#
#         for s in severities:
#             for v in s.values():
#                 severities_count.append(v)
#
#         for status in severity_status:
#             for st in status.values():
#                 severities_status.append(st['Status'])
#
#         return JsonResponse({
#             "module_list" : module_list,
#             "severity_list" : severity_list,
#             "severity_count" : severities_count,
#             "severity_status" : severities_status
#         })
#     else:
#         return JsonResponse({
#             "message" : "HTTP method not allowed"
#         })

# API for Severity by Cycle by Module
# @csrf_exempt
# def severity_by_cycle_by_modules(request):
#     if request.method == 'GET':
#         conn =getConnection()
#         collection = conn['RPAOutput']
#         module_list = list(collection.distinct("Module"))
#         severity_list = list(collection.distinct("Severity"))
#         severity_list = list(filter(None,severity_list))
#         test_cycle_list = list(collection.distinct("Test Cycle"))
#         test_cycle_list = list(filter(None, test_cycle_list))

#         cycleList=[]
#         sevList=[]
#         for module in module_list:
#             for severity in severity_list:
#                 docs_list = list(collection.find({'Actual Result': 'Fail', 'Module': module,'Severity':severity }, {"Test Cycle":1,"_id": 0}))
#                 sev_list = list(collection.find({'Actual Result': 'Fail', 'Module': module, 'Severity': severity},{"Severity": 1, "_id": 0}))
#                 data = json.dumps(docs_list, default=json_util.default)
#                 data = json.loads(data)

#                 sev_data = json.dumps(sev_list, default=json_util.default)
#                 sev_data = json.loads(sev_data)
#                 print(data)
#                 for temp in data:
#                     for v in temp.values():
#                         cycleList.append(v)
#                 for temp in sev_data:
#                     for v in temp.values():
#                         sevList.append(v)

#         return JsonResponse({
#             "module_list": module_list,
#             "severity_list" : sevList,
#             "test_cycle_list":cycleList
#         })
#     else:
#         return JsonResponse({
#             "message" : "HTTP method not allowed"
#         })


# API for Severity by Cycle by Module
@csrf_exempt
def severity_by_cycle_by_modules(request):
    if request.method == 'GET':
        conn =getConnection()
        # collection = conn['rpaInfo']
        collection = conn['rpaInfo']

        module_list = list(collection.distinct("Module"))

        test_cycle_list = list(collection.distinct("Test Cycle #"))
        test_cycle_list = list(filter(None, test_cycle_list))

        final = []

        for module in module_list:
            final_data = {}
            for test_cycle in test_cycle_list:
                pipe = [{'$match': {'Module': module, 'Actual Result': 'Fail', 'Test Cycle #': test_cycle, 'Severity': {'$ne': ''}}},
                        {'$count': 'Severity'}]

                doc_list = list(collection.aggregate(pipeline=pipe))
                dl = json.dumps(doc_list, default=json_util.default)
                dl = json.loads(dl)

                for data in dl:
                    final_data[str(round(test_cycle))]=data['Severity']
            final.append(final_data)

        data = dict(zip(module_list, final))

        return JsonResponse({
            "message" : "success",
            "Module":module_list,
            "data":data
        })
    else:
        return JsonResponse({
            "message" : "HTTP method not allowed"
        })

# API for Success Trend Graph
@csrf_exempt
def success_trend_graph(request):
        conn =getConnection()
        # collection = conn['rpaInfo']
        collection = conn['rpaInfo']

        test_cycle_list = list(collection.distinct("Test Cycle #"))
        test_cycle_list = list(filter(None, test_cycle_list))
        actual_result_list = list(collection.distinct("Actual Result"))
        actual_result_list = list(filter(None, actual_result_list))
        final_test_cycle_list = []

        final=[]
        for testCycle in test_cycle_list:
            final_test_cycle_list.append(round(testCycle))
            temp = {}
            pipe1 = [{'$match': {'Test Cycle #': testCycle}},
                     {'$count': 'Actual Result'}]
            actual_result_count = list(collection.aggregate(pipeline=pipe1))
            total = json.dumps(actual_result_count, default=json_util.default)
            total = json.loads(total)
            print(total)

            for actualResult in actual_result_list:
                pipe = [{'$match': {'Test Cycle #': testCycle, 'Actual Result': actualResult}},
                                {'$count': 'Actual Result'}]
                doc_list = list(collection.aggregate(pipeline=pipe))
                dl = json.dumps(doc_list, default=json_util.default)
                dl = json.loads(dl)

                print('{} : testCycle {} count {}'.format(actualResult,testCycle,dl))
                for data in dl:

                    per=round((int(data['Actual Result'])/(int(total[0]['Actual Result'])))*100)
                    temp[str(actualResult)] = str(per)

            final.append(temp)
        data = dict(zip(final_test_cycle_list, final))
        return JsonResponse({
            "message" : "success",
            "data":data
        })



#API for InfoTile
@csrf_exempt
def infoTileData(request):
    if request.method == 'GET':
        conn=getConnection()
        # collection = conn['rpaInfo']
        collection = conn['rpaInfo']
        #Distinct Modules List
        module_list = list(collection.distinct("Module"))
        severity_list = list(collection.distinct('Severity'))
        severity_list = list(filter(None, severity_list))
        execution_date_list=list(collection.distinct("Execution Date"))
        # log_date_list=list(collection.distinct("Log Date" , { "Log Date" : { '$ne' : '' } } ))

        #Total Actual Count
        countActualResult = [{'$count': 'Actual Result'}]
        countActualResult = list(collection.aggregate(pipeline=countActualResult))

        #High risk Module (Module with most Failed cases)
        high_risk=0
        high_risk_module_final={}
        for module in module_list:
            count = [{'$match': {'Actual Result': "Fail",'Module':module}},
                    {'$count': 'Actual Result'}]
            high_risk_module = list(collection.aggregate(pipeline=count))
            if int(high_risk_module[0]['Actual Result'])>high_risk:
                high_risk=int(high_risk_module[0]['Actual Result'])
                high_risk_module_final[module]=high_risk


        #Test Case Status
        countPass = [{'$match': {'Actual Result': "Pass"}},
                     {'$count': 'Actual Result'}]
        countPass = list(collection.aggregate(pipeline=countPass))
        test_case_status=round(((int(countPass[0]['Actual Result']))/(int(countActualResult[0]['Actual Result']))*100),1)

        # test_case_Velocity
        test_case_velocity=[{'$count': 'Test Case ID'}]
        test_case_velocity= list(collection.aggregate(pipeline=test_case_velocity))
        test_case_velocity=round((int(test_case_velocity[0]['Test Case ID']))/(len(execution_date_list)))

        #Defects Raised Velocity
        pipe = [{'$match': {'Log Date': {'$ne': ''}}},{'$count': 'Log Date'}]
        total_count_log_date=list(collection.aggregate(pipeline=pipe))
        no_of_log_date =list(collection.distinct( "Log Date" , { "Log Date" : { '$ne' : '' } } ))
        defects_raised_velocity=round((int(total_count_log_date[0]['Log Date'])/(int(len(no_of_log_date)))),1)

        # High Severity Defects
        high_severity_defects=0
        if 'Critical' in severity_list and 'High' in severity_list:
            high_pipe = [{'$match': {'Severity':'High'}}, {'$count': 'Severity'}]
            critical_pipe = [{'$match': {'Severity': 'Critical'}}, {'$count': 'Severity'}]

            high_count = list(collection.aggregate(pipeline=high_pipe))
            critical_count = list(collection.aggregate(pipeline=critical_pipe))

            high_severity_defects=(int(high_count[0]['Severity'])+int(critical_count[0]['Severity']))
        elif 'Critical' in severity_list:
            critical_pipe = [{'$match': {'Severity': 'Critical'}}, {'$count': 'Severity'}]
            critical_count = list(collection.aggregate(pipeline=critical_pipe))

            high_severity_defects = (int(critical_count[0]['Severity']))
        elif 'High' in severity_list:
            high_pipe = [{'$match': {'Severity':'High'}}, {'$count': 'Severity'}]
            high_count = list(collection.aggregate(pipeline=high_pipe))
            
            high_severity_defects = (int(critical_count[0]['Severity']))

        return JsonResponse({
            "message": "success",
            "test_case_status": str(test_case_status) + '%',
            "test_case_velocity": test_case_velocity,
            "high_risk_module":high_risk_module_final,
            "defects_raised_velocity":defects_raised_velocity,
            "high_severity_defects":high_severity_defects

        })

    else:
        return JsonResponse({
            "message" : "HTTP method not allowed"
        })

# API For Dashboard Drilldown Defects by Severity
#code owner: Akhilesh Jain
#Date: 17/06/2019
@csrf_exempt
def drill_down_DefectBySeverity(request):
    if request.method == 'GET':
        module = request.GET['module']
        conn = getConnection()
        # collection = conn['rpaInfo']
        collection = conn['rpaInfo']
        if module=='Defect Management':
            dataList = list(collection.find({'Expected Result': 'Pass', 'Actual Result': 'Fail'},
                                            {'SL #': 1, 'Module': 1, 'Test Case ID': 1, 'Scenario ID': 1, 'Test Cycle #': 1,
                                             'Defect No': 1, 'Log Date': 1, 'Severity': 1, 'Details': 1, 'Status': 1,
                                             'Defect Owner': 1, 'Closing Date': 1, '_id': 0}))
            dataList = json.dumps(dataList, default=json_util.default)
            dataList = json.loads(dataList)
            if len(dataList) == 0:
                return JsonResponse({
                    "message": "No Record Found for Module : {}".format(module),
                    "count": len(dataList),
                })
            else:
                return JsonResponse({
                    "message": "success",
                    "count": len(dataList),
                    "data": dataList
                })
        else:
            dataList =list(collection.find({'Module':module,'Expected Result': 'Pass', 'Actual Result': 'Fail'},{'SL #':1,'Module':1,'Test Case ID':1,'Scenario ID':1,'Test Cycle #':1,'Defect No':1,'Log Date':1,'Severity':1,'Details':1,'Status':1,'Defect Owner':1,'Closing Date':1,'_id': 0}))
            dataList = json.dumps(dataList, default=json_util.default)
            dataList = json.loads(dataList)
            if len(dataList)==0:
                return JsonResponse({
                    "message": "No Record Found for Module : {}".format(module),
                    "count": len(dataList),
                })
            else:
                return JsonResponse({
                    "message": "success",
                    "count":len(dataList),
                    "data":dataList
                })
    else:
        return JsonResponse({
            "message": "HTTP {} method not allowed".format(request.method)
        })

# API For Dashboard Drilldown Test Cases
#code owner: Akhilesh Jain
#Date: 18/06/2019
@csrf_exempt
def drill_down_TestCases(request):
    if request.method == 'GET':
        result = request.GET['result']
        conn = getConnection()
        # collection = conn['rpaInfo']
        collection = conn['rpaInfo']
        if result == 'Test Case Management':
            dataList = list(collection.find({}, {'SL #': 1, 'Module': 1, 'Test Case ID': 1, 'Scenario ID': 1, 'Test Cycle #': 1,
                                             'Expected Result': 1, 'User': 1, 'Execution Date': 1, 'Actual Result': 1,
                                             '_id': 0}))
            dataList = json.dumps(dataList, default=json_util.default)
            dataList = json.loads(dataList)
            if len(dataList) == 0:
                return JsonResponse({
                    "message": "No Record Found for Module : {}".format(result),
                    "count": len(dataList),
                })
            else:
                return JsonResponse({
                    "message": "success",
                    "count": len(dataList),
                    "data": dataList
                })
        else:
            dataList =list(collection.find({'Actual Result': result},{'SL #':1,'Module':1,'Test Case ID':1,'Scenario ID':1,'Test Cycle #':1,'Expected Result':1,'User':1,'Execution Date':1,'Actual Result':1,'_id': 0}))
            dataList = json.dumps(dataList, default=json_util.default)
            dataList = json.loads(dataList)
            if len(dataList)==0:
                return JsonResponse({
                    "message": "No Record Found for Module : {}".format(result),
                    "count": len(dataList),
                })
            else:
                return JsonResponse({
                    "message": "success",
                    "count":len(dataList),
                    "data":dataList
                })
    else:
        return JsonResponse({
            "message": "HTTP {} method not allowed".format(request.method)
        })

# API For InfoTile Details for table
#code owner: Akhilesh Jain
#Date: 02/07/2019
@csrf_exempt
def infoTileDataDetails(request):
    if request.method == 'GET':
        result = request.GET['value']
        conn = getConnection()
        # collection = conn['rpaInfo']
        collection = conn['rpaInfo']
        # Distinct Modules List
        module_list = list(collection.distinct("Module"))
        execution_date_list = list(collection.distinct("Execution Date"))
        log_date_list = list(collection.distinct(
            "Log Date", {"Log Date": {'$ne': ''}}))

        # Total Actual Count
        countActualResult = [{'$count': 'Actual Result'}]
        countActualResult = list(
            collection.aggregate(pipeline=countActualResult))

        if result == 'Test Case Status':
            # dataList = list(collection.find(
            #     {'Actual Result': "Pass"}, {'_id': 0, 'SL': 0, 'Failure Justification': 0,'Defect No':0
            #     ,"Log Date":0,"Severity":0,"Details":0,"Status":0,"Defect Owner":0,"Closing Date":0}))
            dataList = list(collection.find(
                {'Actual Result': "Pass"}, {'_id': 0, 'SL': 0}))
            return JsonResponse({
                "message": "success",
                "count":len(dataList),
                "data": dataList,
            })

        elif result == 'Defects Raised Velocity':
            dataList = list(collection.find(
                {'Log Date': {'$ne': ''}}, {'_id': 0, 'SL': 0}))
            return JsonResponse({
                "message": "success",
                "count": len(dataList),
                "data": dataList
            })
        elif result == 'High Risk Module':
            dataList = []
            high_risk = 0
            high_risk_module_final = []
            for module in module_list:
                count = [{'$match': {'Actual Result': "Fail", 'Module': module}},
                         {'$count': 'Actual Result'}]
                high_risk_module = list(collection.aggregate(pipeline=count))

                if int(high_risk_module[0]['Actual Result']) > high_risk:
                    high_risk_module_final.clear()
                    high_risk = int(high_risk_module[0]['Actual Result'])
                    high_risk_module_final = list(collection.find(
                        {'Actual Result': "Fail", 'Module': module}, {'_id': 0, 'SL': 0}))
            return JsonResponse({
                "message": "success",
                "count": len(high_risk_module_final),
                "data": high_risk_module_final
            })
        elif result == 'Test Case Velocity':
            dataList = list(collection.find(
                {'Execution Date': {'$ne': ''}}, {'_id': 0, 'SL': 0}))
            return JsonResponse({
                "message": "success",
                "count": len(dataList),
                "data": dataList
            })
        elif result == 'High Severity Defects':
            dataList = list(collection.find(
                {'Severity': 'High'}, {'_id': 0, 'SL': 0}))
            dataListCritical = list(collection.find(
                {'Severity': 'Critical'}, {'_id': 0, 'SL': 0}))
            dataList.extend(dataListCritical)
            return JsonResponse({
                "message": "success",
                "count": len(dataList),
                "data": dataList
            })
        else:
            return JsonResponse({
                "message": "failed"
            })
    else:
        return JsonResponse({
            "message": "HTTP method not allowed"
        })


# Table Update API
@csrf_exempt
def update_table(request):
    if request.method == 'POST':
        reqData = request.body.decode('utf8')
        table_data = json.loads(reqData)

        # print(type(table_data)

        conn = getConnection()
        collection = conn['rpaInfo']

        for each_table_row in table_data:

            # print(each_table_row['SL #'])

            SL_NO = each_table_row['SL #']
            Severity = each_table_row['Severity']
            Details = each_table_row['Details']
            Status = each_table_row['Status']
            Defect_Owner = each_table_row['Defect Owner']

            docs_list = list(collection.find({'SL #': SL_NO}))
            data = json.dumps(docs_list, default=json_util.default)
            data = json.loads(data)

            if data:
                cond = {
                    "SL #": SL_NO
                }
                data = {
                    "$set": {"Severity": Severity, "Details": Details, "Status": Status, "Defect Owner": Defect_Owner}
                }

                collection.update(cond, data)

            else:
                return JsonResponse({
                    "reason" : "Table Data not Found.",
                    "message": "Failure",
                })
        return JsonResponse({
            "reason" : "Data Updated successfully",
            "message": "Success"
        })
