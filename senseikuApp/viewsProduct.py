from json.decoder import JSONDecodeError
from django.contrib.auth.models import User
from django.db.models import fields, query, Sum
from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import Course, Location, Schedule, Cart, Tracker, Review, Transaction, Wishlist
from django.core import serializers
from django.http import HttpResponse,JsonResponse
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from sklearn.metrics.pairwise import haversine_distances
from math import radians
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

import json

def getNewCourse(request):
    courseList=[*Course.objects.order_by('-id')[:5], *User.objects.order_by('-course__id')[:5]]
    courseData=serializers.serialize(
        'json', courseList,
        fields=('id','course_name','description','pricing','tutor_username','username','first_name')
    )
    return HttpResponse(courseData)

def getMyCourse(request):
    data = request.GET.get('username')
    courseList = Course.objects.filter(tutor_username=data)
    courseData = serializers.serialize(
        'json', courseList, fields=('id','course_name','description','pricing','tutor_username')
    )
    return HttpResponse(courseData)

def getMySchedule(request):
    data = request.GET.get('username')
    scheduleList = list(Schedule.objects.filter(tutor_username=data).values(
        'id','tutor_username','date','hour_start','hour_finish','availability','course_id','finish'
    ))
    for i in range(len(scheduleList)):
        status = list(Cart.objects.filter(schedule_id=scheduleList[i]['id']) \
                                  .values_list('student_username__transaction__status'))
        scheduleList[i]['status'] = None if status == [] else status[0][0]
    return JsonResponse(scheduleList, safe=False)

def getAllCourse(request):
    courseList=[*Course.objects.order_by('id'), *User.objects.order_by('course__id')]
    courseData=serializers.serialize(
        'json', courseList,
        fields=('id','course_name','description','pricing','tutor_username','username','first_name')
    )
    return HttpResponse(courseData)

def getCourseDetail(request):
    data = request.GET.get('id')
    username = Course.objects.filter(id=data).values_list('tutor_username')
    selectedCourse = [*Course.objects.filter(id=data), *User.objects.filter(course__id=data),
                      *Schedule.objects.filter(tutor_username__in=username)]
    serialized = serializers.serialize(
        'json', selectedCourse,
        fields=('course_name','description','pricing','username','first_name',
                'date','hour_start','hour_finish','availability')
    )
    return HttpResponse(serialized)

@csrf_exempt
def addCourse(request):
    data=json.loads(request.body.decode('utf-8'))
    courseDict={
        "course_name":data['course_name'],
        "description":data['description'],
        "pricing":data['pricing'],
        "tutor_username":data['tutor_username'],
        "message":"addCourse success"
    }
    try:
        Course.objects.create(
            course_name=courseDict['course_name'],
            description=courseDict['description'],
            pricing=courseDict['pricing'],
            tutor_username_id=courseDict['tutor_username']
        )
        return JsonResponse(courseDict)
    except IntegrityError:
        courseDict.update(
            {
                "message":"addCourse failed, id already exists"
            }
        )
        return JsonResponse(courseDict, status=404)

@csrf_exempt
def updateCourse(request):
    data=json.loads(request.body.decode('utf-8'))
    courseDict={
        "id":data['id'],
        "course_name":data['course_name'],
        "description":data['description'],
        "pricing":data['pricing'],
        "tutor_username":data['tutor_username'],
        "message":"Update success"
    }
    if Course.objects.filter(id=courseDict['id']).exists():
        Course.objects.filter(id=courseDict['id']).update(
            course_name=courseDict['course_name'],
            description=courseDict['description'],
            pricing=courseDict['pricing'],
            tutor_username_id=courseDict['tutor_username']
        )
        return JsonResponse(courseDict)
    else:
        courseDict.update({
            "message":"Update failed, id not exist"
        })
        return JsonResponse(courseDict, status=404)

@csrf_exempt
def deleteCourse(request):
    data=json.loads(request.body.decode('utf-8'))
    courseDict={
        "id":data['id'],
        "message":""
    }
    if Course.objects.filter(id=courseDict['id']).exists():
        Course.objects.filter(id=courseDict['id']).delete()
        Schedule.objects.filter(course_id=courseDict['id']).delete()
        Review.objects.filter(course_id=courseDict['id']).delete()
        courseDict.update({
            "message":"Delete success"
        })
        return JsonResponse(courseDict)
    else:
        courseDict.update({
            "message":"Delete failed, id not exist"
        })
        return JsonResponse(courseDict, status=404)

@csrf_exempt
def addSchedule(request):
    data=json.loads(request.body.decode('utf-8'))
    
    scheduleDict={
        "tutor_username":data['tutor_username'],
        "date":data['date'],
        "hour_start":data['hour_start'],
        "hour_finish":data['hour_finish'],
        "message":"success"
    }
    try:
        Schedule.objects.create(
            tutor_username_id=scheduleDict['tutor_username'],
            date=scheduleDict['date'],
            hour_start=scheduleDict['hour_start'],
            hour_finish=scheduleDict['hour_finish'],
            availability=True
        )
        return JsonResponse(scheduleDict)
    except IntegrityError:
        scheduleDict['message'] = 'failed'
        return JsonResponse(scheduleDict, status=404)

@csrf_exempt
def updateSchedule(request):
    data=json.loads(request.body.decode('utf-8'))
    
    scheduleDict={
        "id":data['id'],
        "date":data['date'],
        "hour_start":data['hour_start'],
        "hour_finish":data['hour_finish'],
        "message":""
    }
    try:
        Schedule.objects.filter(id=scheduleDict['id']).update(
            date=scheduleDict['date'],
            hour_start=scheduleDict['hour_start'],
            hour_finish=scheduleDict['hour_finish'],
        )
        scheduleDict.update({
            "message":"Update success"
        })
        return JsonResponse(scheduleDict)
    except IntegrityError:
        scheduleDict.update({
            "message":"Update failed, id not exist"
        })
        return JsonResponse(scheduleDict, status=404)

@csrf_exempt
def deleteSchedule(request):
    data=json.loads(request.body.decode('utf-8'))
    scheduleDict={
        "id":data['id'],
        "message":""
    }
    if Schedule.objects.filter(id=scheduleDict['id']).exists():
        Schedule.objects.filter(id=scheduleDict['id']).delete()
        scheduleDict.update({
            "message":"Delete success"
        })
        return JsonResponse(scheduleDict)
    else:
        scheduleDict.update({
            "message":"Delete failed, id not exist"
        })
        return JsonResponse(scheduleDict, status=404)

@csrf_exempt
def addCart(request):
    data = json.loads(request.body.decode('utf-8'))
    cartDict = {
        "student_username": data['student_username'],
        "schedule_id": data['schedule_id'],
        "course_id": data['course_id']
    }
    tutor_username = ''
    student_latitude = 0
    student_longitude = 0
    tutor_latitude = 0
    tutor_longitude = 0
    price = 0
    course_list = list(Course.objects.filter(id=cartDict['course_id']).values(
        'pricing', 'tutor_username'
    ))
    for key in course_list:
        cartDict['course_price'] = key['pricing']
        tutor_username = key['tutor_username']
    student_location = list(Location.objects.filter(username=data['student_username']).values(
        'latitude', 'longitude'
    ))
    for key in student_location:
        student_latitude = key['latitude']
        student_longitude = key['longitude']
    tutor_location = list(Location.objects.filter(username=tutor_username).values(
        'latitude', 'longitude'
    ))
    for key in tutor_location:
        tutor_latitude = key['latitude']
        tutor_longitude = key['longitude']
    if tutor_latitude and tutor_longitude and student_latitude and student_longitude is not None:
        tutor_loc = [tutor_latitude, tutor_longitude]
        student_loc = [student_latitude, student_longitude]
        tutor_loc_rad = [radians(_) for _ in tutor_loc]
        student_loc_rad = [radians(_) for _ in student_loc]
        distance = haversine_distances([tutor_loc_rad, student_loc_rad])
        distance = distance * 6371000/1000
        price = round(5000*distance[0][1])
    cartDict['transport_price'] = price
    cartDict['total_price'] = cartDict['course_price'] + cartDict['transport_price']
    try:
        Cart.objects.create(
            student_username_id = cartDict['student_username'],
            schedule_id_id = cartDict['schedule_id'],
            course_id_id = cartDict['course_id'],
            course_price = cartDict['course_price'],
            transport_price = cartDict['transport_price'],
            total_price = cartDict['total_price']
        )
        Schedule.objects.filter(id=data['schedule_id']).update(
            availability = False,
            course_id = cartDict['course_id']
        )
        cartDict['message'] = "success"
        return JsonResponse(cartDict)
    except IntegrityError:
        cartDict['message'] = "failed"
        return JsonResponse(cartDict, status=404)

def getMyCart(request):
    data = request.GET.get('username')
    if Cart.objects.filter(student_username=data).exists():
        cartList = list(Cart.objects.filter(student_username=data).values(
            'id','student_username','course_id','course_id__course_name',
            'course_id__description','course_price',
            'course_id__tutor_username','course_id__tutor_username__first_name',
            'schedule_id','schedule_id__date',
            'schedule_id__hour_start','schedule_id__hour_finish',
            'transport_price','total_price', 'time_checked_out'
        ))
        for key in cartList:
            key['course_name'] = key.pop('course_id__course_name')
            key['description'] = key.pop('course_id__description')
            key['tutor_username'] = key.pop('course_id__tutor_username')
            key['first_name'] = key.pop('course_id__tutor_username__first_name')
            key['date'] = key.pop('schedule_id__date')
            key['hour_start'] = key.pop('schedule_id__hour_start')
            key['hour_finish'] = key.pop('schedule_id__hour_finish')
    else:
        cartList = {'student_username': data, 'message': 'empty cart'}
    return JsonResponse(cartList, safe=False)

# delete all cart
@csrf_exempt
def deleteMyCart(request):
    data = request.GET.get('username')
    output={
        "message":"remove success"
    }
    filtered = Cart.objects.filter(student_username=data)
    if filtered.exists():
        for i in range(len(list(filtered))):
            Schedule.objects.filter(id=filtered.values_list('schedule_id')[i][0]).update(availability=True)
        filtered.delete()
        return JsonResponse(output,status=200)
    else:
        output['message']="already empty"
        return JsonResponse(output,status=404)

# delete only one cart
@csrf_exempt
def deleteCart(request):
    data = request.GET.get('id')
    output={
        "message":"remove success"
    }
    filtered = Cart.objects.filter(id=data)
    if filtered.exists():
        Schedule.objects.filter(id=filtered.values_list('schedule_id')[0][0]) \
                        .update(availability=True)
        filtered.delete()
        return JsonResponse(output,status=200)
    else:
        output['message']="cart deleted"
        return JsonResponse(output,status=404)

@csrf_exempt
def tracker(request):
    data=json.loads(request.body.decode('utf-8'))
    trackerDict={
        "course_id":data['course_id'],
        "username":data['username'],
        "event":data['event'],
        "timestamp":data['timestamp']
    }
    statusDict={
        "message":"success"
    }
    try:
        Tracker.objects.create(
            course_id_id=trackerDict['course_id'],
            username_id=trackerDict['username'],
            event=trackerDict['event'],
            timestamp=trackerDict['timestamp']
        )
        return JsonResponse(statusDict, status=200)
    except IntegrityError:
        statusDict['message']="failed"
        return JsonResponse(statusDict, status=404)
        
@csrf_exempt
def addTransaction(request):
    data=json.loads(request.body.decode('utf-8'))
    transactionTotalPrice=Cart.objects.filter(student_username=data['student_username']).aggregate(Sum('total_price'))

    sumResult=transactionTotalPrice.get('total_price__sum')
    if sumResult==None:
        sumResult=0

    statusDict={
        "message":"success"
    }
    try:
        Transaction.objects.create(
            student_username_id=data['student_username'],
            timestamp=data['timestamp'],
            total_price=sumResult
        )
        Cart.objects.filter(student_username=data['student_username']).update(
            time_checked_out=data['timestamp']
        )
        return JsonResponse(statusDict, status=200)
    except IntegrityError:
        statusDict['message']="failed"
        return JsonResponse(statusDict, status=404)

def getTransactions(request):
    data = request.GET.get('username')
    if Transaction.objects.filter(student_username=data).exists():
        transactionList = list(Transaction.objects.filter(student_username=data).values(
            'id','total_price','timestamp','status','gopay'
        ))
        time = []
        for key in transactionList:
            time.append(key['timestamp'])
        length = len(transactionList)
        for key in range(length):
            transactionList[key].update({
                'courses': list(Cart.objects.filter(time_checked_out=time[key], student_username=data).values(
                    'course_id', 'course_id__course_name','total_price','schedule_id'
                ))
            })
            x=transactionList[key].get('courses')
            for i in x:
                y=Schedule.objects.filter(id=i.get('schedule_id')).values('finish')
                y=y[0].get('finish')
                i['finish']=y
                

    else:
        transactionList = {'student_username': data, 'message': 'no transaction'}
    return JsonResponse(transactionList, safe=False)

@csrf_exempt
def confirmPayment(request):
    data=json.loads(request.body.decode('utf-8'))
    confirmDict={
        "message":""
    }
    try:
        Transaction.objects.filter(id=data['id']).update(
            status="pending",
            gopay=data['gopay']
        )
        confirmDict.update({
            "message":"system is checking payment"
        })
        return JsonResponse(confirmDict)
    except IntegrityError:
        confirmDict.update({
            "message":"Payment failed, id not exist"
        })
        return JsonResponse(confirmDict, status=404)

def confirmFinish(request):
    data = request.GET.get('id')
    confirmDict={
        "message":""
    }
    try:
        Schedule.objects.filter(id=data).update(
            finish=True
        )
        confirmDict.update({
            "message": "Teaching finished"
        })
        return JsonResponse(confirmDict)
    except IntegrityError:
        confirmDict.update({
            "message": "Confirmation failed"
        })
        return JsonResponse(confirmDict, status=404)

def getWishlist(request):
    data = request.GET.get('username')
    if Wishlist.objects.filter(student_username=data).exists():
        wishlistList=list(Wishlist.objects.filter(student_username=data).values('course_id'))
        courseList=[]
        for i in wishlistList:
            courseList.append((Course.objects.filter(id=i.get('course_id')) \
                .values('id','course_name','description','pricing','tutor_username__first_name'))[0])
        outputDict={
            "username":data,
            "course_list":(courseList),
            "message":"success"
        }
        return JsonResponse(outputDict,status=200)
    outputDict={
            "username":data,
            "message":"failed"
        }
    return JsonResponse(outputDict,status=404)
    
@csrf_exempt
def addWishlist(request):
    data = json.loads(request.body.decode('utf-8'))
    wishlist_dict = {
        'course_id': data['course_id'],
        'username': data['username'],
        'message': 'success'
    }
    try:
        Wishlist.objects.create(
            course_id_id = wishlist_dict['course_id'],
            student_username_id = wishlist_dict['username']
        )
        return JsonResponse(wishlist_dict, status=200)
    except IntegrityError:
        wishlist_dict['message'] = 'failed'
        return JsonResponse(wishlist_dict, status=404)

@csrf_exempt
def deleteWishlist(request):
    data = request.GET.copy()
    output = {'message': 'remove success'}
    if Wishlist.objects.filter(student_username=data['username'],
                               course_id=data['course_id']).exists():
        Wishlist.objects.filter(student_username=data['username'],
                                course_id=data['course_id']).delete()
        return JsonResponse(output, status=200)
    else:
        output['message'] = "wishlist doesn't exist"
        return JsonResponse(output, status=404)

def adminGetTransactions(request):
    data = request.GET.get('username')
    if data == 'admin':
        transactionList = list(Transaction.objects.values(
            'id','student_username','total_price','timestamp','status','gopay'
        ))
        for i in range(len(transactionList)):
            courses = list(Cart.objects.filter(
                    time_checked_out=transactionList[i]['timestamp'],
                    student_username=transactionList[i]['student_username']
                ).values('course_id', 'total_price', 'schedule_id')
            )
            for course in courses:
                tutor = list(Course.objects.filter(id=course['course_id']).values(
                    'tutor_username__first_name', 'tutor_username__phone__phone_number'
                ))
                course['tutor_name'] = tutor[0]['tutor_username__first_name']
                course['phone_number'] = tutor[0]['tutor_username__phone__phone_number']
                course['finish'] = Schedule.objects.filter(
                                        id=course.pop('schedule_id')
                                    ).values_list('finish')[0][0]
            transactionList[i]['courses'] = courses
    else:
        transactionList = {'message': 'not admin'}
    return JsonResponse(transactionList, safe=False)

@csrf_exempt
def editStatus(request):
    data = json.loads(request.body.decode('utf-8'))
    try:
        Transaction.objects.filter(id=data['id']).update(status=data['status'])
        data['message'] = 'success'
    except IntegrityError:
        data['message'] = "failed, id doesn't exist"
    return JsonResponse(data)
