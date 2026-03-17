from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.home,                      name='home'),
    path('jobs/',                               views.job_list,                  name='job_list'),
    path('jobs/post/',                          views.post_job,                  name='post_job'),
    path('jobs/<int:pk>/',                      views.job_detail,                name='job_detail'),
    path('jobs/<int:pk>/apply/',                views.apply_job,                 name='apply_job'),
    path('jobs/<int:pk>/edit/',                 views.edit_job,                  name='edit_job'),
    path('jobs/<int:pk>/delete/',               views.delete_job,                name='delete_job'),
    path('jobs/<int:pk>/save/',                 views.toggle_save_job,           name='save_job'),
    path('application/<int:pk>/status/',        views.update_application_status, name='update_status'),
    path('dashboard/',                          views.dashboard,                 name='dashboard'),
    path('profile/edit/',                       views.edit_profile,              name='edit_profile'),
    path('accounts/register/',                  views.register_view,             name='register'),
    path('accounts/login/',                     views.login_view,                name='login'),
    path('accounts/logout/',                    views.logout_view,               name='logout'),
    path('api/search-suggestions/',             views.search_suggestions,        name='search_suggestions'),
    path('api/location-suggestions/',           views.location_suggestions,      name='location_suggestions'),
]
