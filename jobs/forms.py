from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Job, Application, Company

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[('jobseeker','Job Seeker'),('employer','Employer')])
    company_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=15, required=False)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2','role','company_name','phone']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                company_name=self.cleaned_data.get('company_name',''),
                phone=self.cleaned_data.get('phone',''),
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = ['avatar','bio','phone','location','skills','experience_years','linkedin','github','website','resume']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.TextInput(attrs={'placeholder': 'e.g. Python, Django, React'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            user = profile.user
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save()
        return profile


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name','logo','description','website','industry','size','location','founded']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title','company','company_logo','location','description','requirements','salary','job_type','experience','skills_required','deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 5}),
            'skills_required': forms.TextInput(attrs={'placeholder': 'e.g. Python, Django, PostgreSQL'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {'cover_letter': forms.Textarea(attrs={'rows': 6})}


class SaveJobForm(forms.Form):
    job_id = forms.IntegerField(widget=forms.HiddenInput)
