from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Job, Application, UserProfile, SavedJob
from .forms import RegisterForm, JobForm, ApplicationForm


def home(request):
    recent_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:6]
    total_jobs  = Job.objects.filter(is_active=True).count()
    return render(request, 'home.html', {
        'recent_jobs': recent_jobs,
        'total_jobs':  total_jobs,
    })


def job_list(request):
    jobs     = Job.objects.filter(is_active=True)
    query    = request.GET.get('q', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(company__icontains=query) | Q(description__icontains=query))
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    return render(request, 'jobs/job_list.html', {
        'jobs':     jobs,
        'count':    jobs.count(),
        'query':    query,
        'location': location,
        'job_type': job_type,
    })


def job_detail(request, pk):
    job         = get_object_or_404(Job, pk=pk, is_active=True)
    has_applied = False
    is_saved    = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
        is_saved    = SavedJob.objects.filter(job=job, user=request.user).exists()
    job.views_count = job.views_count + 1 if hasattr(job, 'views_count') else 0
    job.save(update_fields=['views_count']) if hasattr(job, 'views_count') else None
    return render(request, 'jobs/job_detail.html', {
        'job':         job,
        'has_applied': has_applied,
        'is_saved':    is_saved,
    })


@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    try:
        profile = request.user.profile
        if profile.role == 'employer':
            messages.error(request, 'Employers cannot apply for jobs.')
            return redirect('job_detail', pk=pk)
    except UserProfile.DoesNotExist:
        pass
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.job       = job
            app.applicant = request.user
            if 'resume' in request.FILES:
                app.resume = request.FILES['resume']
            app.save()
            messages.success(request, f'Application submitted successfully for {job.title}!')
            return redirect('dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})


@login_required
def post_job(request):
    try:
        profile = request.user.profile
        if profile.role != 'employer':
            messages.error(request, 'Only employers can post jobs. Please update your profile role.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('edit_profile')
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job           = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form, 'editing': False})


@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/post_job.html', {'form': form, 'editing': True, 'job': job})


@login_required
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    job.delete()
    messages.success(request, 'Job deleted successfully.')
    return redirect('dashboard')


@login_required
def toggle_save_job(request, pk):
    job  = get_object_or_404(Job, pk=pk)
    obj  = SavedJob.objects.filter(job=job, user=request.user)
    if obj.exists():
        obj.delete()
        messages.info(request, 'Job removed from saved list.')
    else:
        SavedJob.objects.create(job=job, user=request.user)
        messages.success(request, 'Job saved successfully!')
    return redirect(request.META.get('HTTP_REFERER', 'job_list'))


@login_required
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, job__posted_by=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['pending', 'reviewed', 'shortlisted', 'accepted', 'rejected']:
            application.status = status
            application.save()
            messages.success(request, 'Application status updated.')
    return redirect('dashboard')


@login_required
def dashboard(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if profile.role == 'employer':
        my_jobs      = Job.objects.filter(posted_by=request.user).order_by('-created_at')
        applications = Application.objects.filter(job__posted_by=request.user).order_by('-applied_at').select_related('applicant', 'job')
        return render(request, 'accounts/dashboard.html', {
            'my_jobs':      my_jobs,
            'applications': applications,
            'role':         'employer',
        })
    else:
        my_applications = Application.objects.filter(applicant=request.user).order_by('-applied_at').select_related('job')
        saved_jobs      = SavedJob.objects.filter(user=request.user).order_by('-saved_at').select_related('job')
        return render(request, 'accounts/dashboard.html', {
            'my_applications': my_applications,
            'saved_jobs':      saved_jobs,
            'role':            'jobseeker',
        })


@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        # Avatar
        if 'avatar' in request.FILES:
            if profile.avatar:
                try:
                    import os
                    if os.path.isfile(profile.avatar.path):
                        os.remove(profile.avatar.path)
                except Exception:
                    pass
            profile.avatar = request.FILES['avatar']
        # Resume
        if 'resume' in request.FILES:
            profile.resume = request.FILES['resume']
        # User model fields
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name  = request.POST.get('last_name', '').strip()
        request.user.email      = request.POST.get('email', '').strip()
        request.user.save()
        # Profile fields
        profile.phone        = request.POST.get('phone', '').strip()
        profile.location     = request.POST.get('location', '').strip()
        profile.bio          = request.POST.get('bio', '').strip()
        profile.skills       = request.POST.get('skills', '').strip()
        profile.linkedin     = request.POST.get('linkedin', '').strip()
        profile.github       = request.POST.get('github', '').strip()
        profile.website      = request.POST.get('website', '').strip()
        profile.company_name = request.POST.get('company_name', '').strip()
        exp = request.POST.get('experience_years', '').strip()
        if exp.isdigit():
            profile.experience_years = int(exp)
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')

    return render(request, 'accounts/edit_profile.html', {
        'profile': profile,
        'user':    request.user,
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to JobConnect, {user.username}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.GET.get('next', 'home'))
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def search_suggestions(request):
    query       = request.GET.get('q', '').strip()
    suggestions = []
    if len(query) >= 2:
        titles    = Job.objects.filter(title__icontains=query,    is_active=True).values_list('title',    flat=True).distinct()[:5]
        companies = Job.objects.filter(company__icontains=query,  is_active=True).values_list('company',  flat=True).distinct()[:3]
        locations = Job.objects.filter(location__icontains=query, is_active=True).values_list('location', flat=True).distinct()[:3]
        for t in titles:    suggestions.append({'type': 'title',    'value': t, 'icon': 'briefcase'})
        for c in companies: suggestions.append({'type': 'company',  'value': c, 'icon': 'building'})
        for l in locations: suggestions.append({'type': 'location', 'value': l, 'icon': 'geo-alt'})
    return JsonResponse({'suggestions': suggestions})


def location_suggestions(request):
    query = request.GET.get('q', '').strip()
    locs  = []
    if len(query) >= 2:
        locs = list(Job.objects.filter(location__icontains=query, is_active=True).values_list('location', flat=True).distinct()[:6])
    return JsonResponse({'locations': locs})
