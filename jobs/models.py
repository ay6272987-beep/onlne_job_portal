from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [('employer', 'Employer'), ('jobseeker', 'Job Seeker')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='jobseeker')
    phone = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.CharField(max_length=300, blank=True, help_text="Comma separated skills")
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    def get_skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []


class Company(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    founded = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_logo_url(self):
        if self.logo:
            return self.logo.url
        return None


class Job(models.Model):
    JOB_TYPE_CHOICES = [('full-time','Full Time'),('part-time','Part Time'),('remote','Remote'),('internship','Internship'),('contract','Contract')]
    EXPERIENCE_CHOICES = [('fresher','Fresher'),('1-2','1-2 Years'),('3-5','3-5 Years'),('5-10','5-10 Years'),('10+','10+ Years')]
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    company_logo = models.ImageField(upload_to='job_logos/', blank=True, null=True)
    location = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField()
    salary = models.CharField(max_length=50, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='fresher')
    skills_required = models.CharField(max_length=300, blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_skills_list(self):
        if self.skills_required:
            return [s.strip() for s in self.skills_required.split(',') if s.strip()]
        return []

    def get_logo_url(self):
        if self.company_logo:
            return self.company_logo.url
        return None


class Application(models.Model):
    STATUS_CHOICES = [('pending','Pending'),('reviewed','Reviewed'),('shortlisted','Shortlisted'),('accepted','Accepted'),('rejected','Rejected')]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'job']

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
