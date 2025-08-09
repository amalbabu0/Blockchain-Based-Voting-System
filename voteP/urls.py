from voteA import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('student_register/', views.student_registration, name='student_register'),
    path('student_home/', views.student_home, name='student_home'),
    path('student_details_view/', views.student_details_view, name='student_details_view'),
    path('student_profile/', views.student_profile, name='student_profile'),
    path('staff_register/', views.staff_register, name='staff_register'),
    path('staff_home/', views.staff_home, name='staff_home'),
    path('staff2_home/', views.staff2_home, name='staff2_home'),
    path('candidate_home/', views.candidate_home, name='candidate_home'),
    path('candidate_profile/', views.candidate_profile, name='candidate_profile'),
    path('candidate_registration/', views.candidate_registration, name='candidate_registration'),
    path('manage_student/', views.manage_student, name='manage_student'),
    path('manage_studentStaff/', views.manage_studentStaff, name='manage_studentStaff'),
    path('manage_staff/', views.manage_staff, name='manage_staff'),
    path('manage_candidate/', views.manage_candidate, name='manage_candidate'),
    path('manage_candidate/<int:student_id>/reject/', views.reject_candidate, name='reject_candidate'),
    path('accept_student/<int:student_id>/', views.accept_student, name='accept_student'),
    path('accept_staff/<int:staff_id>/', views.accept_staff, name='accept_staff'),
    path('accept_candidate/<int:students_ad_no>/', views.accept_candidate, name='accept_candidate'),
    path('reject_student/<int:student_id>/', views.reject_student, name='reject_student'),
    path('reject_staff/<int:staff_id>/', views.reject_staff, name='reject_staff'),
    path('blog/', views.blog, name='blog'),
    path('blogs/', views.view_blog, name='view_blog'),
    path('view_candidates/', views.view_candidates, name='view_candidates'),
    path('view_students/', views.view_students, name='view_students'),
    path('result/', views.result, name='result'),
    path('result1/', views.result1, name='result1'),
    path('election/', views.election, name='election'),
    path('election2/', views.election2, name='election2'),
    path('admin/', admin.site.urls),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('Feed/', views.Feed, name='Feed'),
    path('get_student_details/', views.get_student_details, name='get_student_details'),
    path('', views.index, name='index'),
    path('right/', views.right, name='right'),
    path('login/', views.login, name='login'),
    path('vote/<int:candidate_id>/', views.vote, name='vote'),
    path('start_vote', views.start_vote, name='start_vote'),
    path('top-candidates/', views.top_candidates_view, name='top_candidates'),
    path('newvote/', views.newvote, name='newvote'),
    path('update_top_candidates/', views.update_top_candidates, name='update_top_candidates'),
    path('classrep/', views.classrep, name='classrep'),
    path('campusvote/', views.campusvote, name='campusvote'),
    path('vote/', views.campusvote, name='vote'),
    path('result_view/', views.result_view, name='result_view'),
    path('chat/', views.chatbot_view, name='chatbot'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




