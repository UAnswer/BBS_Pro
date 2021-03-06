from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User

from django.contrib import comments
from django.contrib.contenttypes.models import ContentType
import models
import datetime

# Create your views below
def acc_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = auth.authenticate(username=username, password=password)
    print username,'->',password
    
    if user is not None:
        auth.login(request,user)
        
        return HttpResponseRedirect('/')
    else:
        return render_to_response('login.html',{'login_err':'Wrong username or password.'})

def reset_password(request, username, password):
    u = User.objects.get(username__exact = username)
    u.set_password(password)
    u.save() 

def Register(request):
    return render_to_response('register.html')

def acc_register(request):
    new_username = request.POST.get('username')
    new_password = request.POST.get('password')
    
    found = False
    if User.objects.filter(username = new_username).count():
        found = True
    else:
        found = False
        
    if found:
        return render_to_response('register.html',{'register_err':'Username already exists'})

    else:
        
        new_user = User.objects.create_user(
                                    username = new_username,
                                    password = new_password
                                    )
        
        new_user.save()
    
        user = auth.authenticate(   username=new_username, 
                                    password=new_password
                                )
        
        auth.login(request,user)
        
        return HttpResponseRedirect('/')

def logout_view(request):
    user = request.user
    auth.logout(request)

    return render_to_response('logout.html',{'username':user})
#     return HttpResponse("    \
#             <b>%s</b> logged out! <br/>    \
#             <a href = '/'>log in again</a>" 
#             %user
#         )

def Login(request):
    return render_to_response('login.html')

def index(request):
    bbs_list = models.BBS.objects.all()
    bbs_categories = models.Category.objects.all()

    return render_to_response('index.html',{
                                            'bbs_list':bbs_list,
                                            'user':request.user,
                                            'bbs_category':bbs_categories,
                                            'category_id':0
                                            })

def category(request, cate_id):
    bbs_list = models.BBS.objects.filter(category__id = cate_id)
    bbs_categories = models.Category.objects.all()
    
    return render_to_response('index.html',{
                                            'bbs_list':bbs_list,
                                            'user':request.user,
                                            'bbs_category':bbs_categories,
                                            'category_id':int(cate_id)
                                            })

def bbs_detail(request, bbs_id):
    bbs_obj = models.BBS.objects.get(id = bbs_id)
    return render_to_response('bbs_detail.html', {'bbs_obj':bbs_obj,'user':request.user}, context_instance = RequestContext(request))

def sub_comment(request):
    bbs_id = request.POST.get('bbs_id')
    comment = request.POST.get('comment_content')
    
    # Write comment to DB
    # Be careful about the names of the following parameters. 
    # Check django.contrib.contenttypes.models source code if necessary.
    comments.models.Comment.objects.create(
          content_type_id = 7,
          object_pk = bbs_id,   # Not object_id which is very confusing
          site_id = 1,
          user = request.user,
          comment = comment,)
    
    return HttpResponseRedirect('/detail/%s'%bbs_id)

def bbs_pub(request):
    bbs_categories = models.Category.objects.all()
    return render_to_response('bbs_pub.html',{
                                            'bbs_pub':1,
                                            'bbs_category':bbs_categories,
                                            })

def submit_bbs(request):
    print request.POST
    print models.BBS_user
    
    bbs_category = request.POST.get('bbs_category')
    models.BBS.objects.create(
        title = request.POST.get('title'),
        category = models.Category.objects.get(name = bbs_category),
        content = request.POST.get('content'),
        author = models.BBS_user.objects.get(user_username = 'root'),
        modify_date = datetime.datetime.now()
    )
    bbs_content = request.POST.get('content')
    return HttpResponse('Your article has been submitted!')

def bbs_sub(request):
    content = request.POST.get('content')
    print "content -->", content
    
    category_select_index = request.POST.get('category_select')
    bbs_categories = models.Category.objects.all()
    category_select = bbs_categories[int(category_select_index)]
      
    title = request.POST.get('title')
    
    summary = request.POST.get('summary')
    
    category = models.Category.objects.get(name = category_select) 
    
    author = models.BBS_user.objects.get(user__username = request.user)
    
    models.BBS.objects.create(
        title = title,
        summary = summary,
        content = content,
        author = author,    # Save by parameter name
        category = category,    # Save by parameter id (number)
        view_count = 1,
        ranking = 1,  
    )

    return HttpResponseRedirect('/')
