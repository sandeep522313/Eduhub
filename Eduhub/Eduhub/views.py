from django.contrib import messages
from django.shortcuts import render,redirect
from app.models import Categories,Course,Level,Video,UserCourse,Student

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from Eduhub.settings import ROZORPAY_API_SECRET_KEY,ROZORPAY_API_KEY
import razorpay
from django.conf import settings



def BASE(request):
    return render(request,'base.html')

def HOME(request):
    category=Categories.objects.all().order_by('id')[0:6]
    course=Course.objects.filter(status='PUBLISH').order_by('id')
    context={
        'category':category,
        'course':course
    }
    return render(request,'main/home.html',context)
@login_required
def SINGLE_COURSE(request):
    category=Categories.get_all_category(Categories)
    level=Level.objects.all
    course=Course.objects.all()
    FreeCourse_count=Course.objects.filter(price=0).count()
    PaidCourse_count=Course.objects.filter(price__gte=1).count()
    context={
        'category':category,
        'level':level,
        'course':course,
        'FreeCourse_count':FreeCourse_count,
        'PaidCourse_count':PaidCourse_count
    }
    return render(request,'main/single_course.html',context)

def filter_data(request):
    category=request.GET.getlist('category[]')
    level=request.GET.getlist('level[]')
    price=request.GET.getlist('price[]')
   
    if price == ['pricefree']:
       course = Course.objects.filter(price=0)
    elif price == ['pricepaid']:
       course = Course.objects.filter(price__gte=1)
    elif price == ['priceall']:
       course = Course.objects.all()
    elif category:
        course=Course.objects.filter(category__id__in=category).order_by('-id')
    elif level:
        course=Course.objects.filter(level__id__in=level).order_by('-id')
    else:
        course=Course.objects.all().order_by('-id')
    
    context={
        'course':course
    }
    t = render_to_string('ajax/course.html',context)

    return JsonResponse({'data': t})

    

def CONTACT_US(request):
    category=Categories.get_all_category(Categories)
    context={
        'category':category,
    }
    
    return render(request,'main/contact_us.html',context)

def ABOUT_US(request):
    category=Categories.get_all_category(Categories)
    student=Student.objects.all()
    context={
        'category':category,
        'student':student
    }
    return render(request,'main/about_us.html',context)

def SEARCH_COURSE(request):
    category=Categories.get_all_category(Categories)
    


    query=request.GET['query']
    course=Course.objects.filter(title__icontains=query)
    context={
        'course':course,
        'category':category
    }
    return render(request,'search/search.html',context)
@login_required
def COURSE_DETAILS(request,slug):

    category=Categories.get_all_category(Categories)
    time_duration=Video.objects.filter(course__slug=slug).aggregate(sum=Sum('time_duration'))
    
    course_id=Course.objects.get(slug=slug)
    try:
        check_enroll=UserCourse.objects.get(user=request.user,course=course_id)
    except UserCourse.DoesNotExist:
        check_enroll=None

    course=Course.objects.filter(slug=slug)
    if course.exists():
        course=course.first()
    else:
        return redirect('404')
    
    context={
        'course':course,
        'category':category,
        'time_duration':time_duration,
        'check_enroll':check_enroll,
    }
    return render(request,'course/course_detail.html',context)

def PAGE_NOT_FOUND(request):
    category=Categories.get_all_category(Categories)
    context={
        'category':category
    }
    return render (request,'error/404.html',context)
client = razorpay.Client(auth=(settings.ROZORPAY_API_KEY, settings.ROZORPAY_API_SECRET_KEY))
def CHECKOUT(request,slug):
        course=Course.objects.get(slug=slug)
        print("this >",course.slug)
        if course.price == 0:
            course=UserCourse(
                user=request.user,
                course=course,

            )
            course.save()
            messages.success(request,"Course are successfully Enrolled !")
            return redirect('my_course')
        else:
            order_amount=(course.price*100)-3000
            order_currency='INR'
            order_receipt='order_rcptid_11'
            notes={'shiping address':'Amritsar'}
            order=client.order.create(dict(amount=order_amount,currency=order_currency,receipt=order_receipt,notes=notes))
        context={
        'course':course,
        'api_key':settings.ROZORPAY_API_KEY,
        'order_id':order['id']
        }
        return render(request,'checkout/checkout.html',context)
def payment_done(request,slug):
    print("that <",slug)
    course=Course.objects.get(slug=slug)
    course=UserCourse(
                user=request.user,
                course=course,

            )
    print(course)
    course.save()
    messages.success(request,"Course are successfully Enrolled !")
    return redirect('my_course')
@login_required
def MY_COURSE(request):
    category=Categories.objects.all().order_by('id')
    course=UserCourse.objects.filter(user=request.user)
    context={
        'course':course,
        'category':category,
    }
    return render(request,'course/my-course.html',context)

