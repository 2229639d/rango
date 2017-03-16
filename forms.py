from django import forms
from django.contrib.auth.models import User
from rango.models import Category, Page, UserProfile

class SubjectForm(forms.ModelForm):
	name = forms.CharField(max_length=128, help_text="Please enter the subject name")
	slug = forms.CharField(widget=forms.HiddenInput(), required=False)

	class Meta:
		model = Subject
		fields = ('name',)

class CourseForm(forms.ModelForm):
    name = forms.CharField(max_length=128, 
                            help_text="Please enter the name of the course")
    url = forms.URLField(max_length=200, 
                         help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    
    class Meta:
        model = Page
        exclude = ('category',)
        # or specify the fields to include (i.e. not include the category field)
        #fields = ('title', 'url', 'views')
	def clean(self):
		cleaned_data = self.cleaned_data
		url = cleaned_data.get('url')
		
		if url and not url.startswith('http://'):
			url = 'http://' + url
			cleaned_data['url'] = url
			
			return cleaned_data
			
class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = User
		fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ('website', 'picture')