from django.shortcuts import render
from noodleApp.models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime

def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val


def visitor_cookie_handler(request):
	visits = int(get_server_side_cookie(request, 'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")
	if (datetime.now() - last_visit_time).seconds > 0:
		visits = visits + 1
		request.session['last_visit'] = str(datetime.now())
	else:
		visits = 1
		request.session['last_visit'] = last_visit_cookie
	request.session['visits'] = visits

def index(request):
	request.session.set_test_cookie()
	category_list = Course.objects
	context_dict = {'subject': subject_list}
	
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']
	
	response = render(request, 'noodle/index.html', context=context_dict)
	return response
	
def about(request):

	visitor_cookie_handler(request)
	context_dict = {}
	context_dict['visits'] = request.session['visits']
	print(request.method)
	print(request.user)
	return render(request, 'noodle/about.html',context=context_dict)

def show_category(request, category_name_slug):
	context_dict = {}
	try:
		category = Category.objects.get(slug=category_name_slug)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		context_dict['category'] = None
		context_dict['pages'] = None
	return render(request, 'noodle/category.html', context_dict)
	
def add_subject(request):
	form = CategoryForm()
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			cat = form.save(commit=True)
			print(cat, cat.slug)
			return index(request)
		else:
			print(form.errors)
	return render(request, 'noodle/add_category.html', {'form': form})

def add_course(request, subject_name_slug):
    try:
        course =  Course.objects.get(slug=subject_name_slug)
    except Course.DoesNotExist:
        course = None
    
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if subject:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    
    context_dict = {'form':form, 'category': category}
    return render(request, 'noodle/add_page.html', context_dict)

def register(request):
	registered = False
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered = True
		else:
			print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	return render(request, 'noodle/register.html',
		{'user_form': user_form,
		'profile_form': profile_form,
		'registered': registered})

def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
				return HttpResponse("Your Noodle account is disabled.")
		else:
			print("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details supplied. Invalid username or password.")
	else:
		return render(request, 'noodle/login.html', {})
		
@login_required
def restricted(request):
	return render(request, 'noodle/restricted.html', {})
	
@login_required
def user_logout(request):
	# Since we know the user is logged in, we can now just log them out.
	logout(request)
	# Take the user back to the homepage.
	return HttpResponseRedirect(reverse('index'))
**//