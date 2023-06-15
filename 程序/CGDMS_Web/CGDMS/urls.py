"""
URL configuration for CGDMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
                  # 通用模块
                  path('', views.login_page),
                  path('comment/', views.comment),
                  path('login/', views.login),
                  path('logout/', views.logout),
                  path('register/', views.register),
                  path('index/', views.index),
                  path('showinfo/', views.showinfo),
                  path('account/', views.account),
                  path('change_password/', views.change_password),
                  # 学生模块
                  path('student/', views.student),
                  path('student/project_selection/', views.project_selection),
                  path('student/project_selection/select/', views.select_project),
                  path('student/project_selection/cancel/', views.cancel_select),
                  path('student/browse_task/', views.browse_task),
                  path('student/open_report/', views.open_report),
                  path('student/open_report/submit_report/', views.submit_report),
                  path('student/mid_term_check/', views.mid_term_check),
                  path('student/mid_term_check/submit_progress/', views.submit_progress),
                  path('student/weekly_report/', views.weekly_report),
                  path('student/weekly_report/submit_report/', views.submit_weekly_report),
                  path('student/thesis_draft/', views.thesis_draft),
                  path('student/thesis_draft/submit_draft/', views.submit_draft),
                  path('student/thesis_final/', views.thesis_final),
                  path('student/thesis_final/submit_final/', views.submit_final),
                  path('student/defense_info/', views.defense_info),
                  # 教师模块
                  path('teacher/', views.teacher),
                  path('teacher/role/', views.role),
                  path('teacher/information_summary/', views.information_summary),
                  path('teacher/user_summary/', views.user_summary),
                  # 指导教师模块
                  path('teacher/supervisor/', views.supervisor),
                  path('teacher/supervisor/project_proposal/', views.project_proposal),
                  path('teacher/supervisor/project_proposal/proposal/', views.propose_project),
                  path('teacher/supervisor/project_confirmation/', views.project_confirmation),
                  path('teacher/supervisor/project_confirmation/confirm_project/', views.confirm_project),
                  path('teacher/supervisor/project_confirmation/cancel_pre_selection/', views.cancel_pre_selection),
                  path('teacher/supervisor/project_confirmation/cancel_selection/', views.cancel_confirm),
                  path('teacher/supervisor/task_issue/', views.task_issue),
                  path('teacher/supervisor/task_issue/issue_task/', views.issue_task),
                  path('teacher/supervisor/report_review/', views.report_review),
                  path('teacher/supervisor/report_review/pass_report/', views.pass_report),
                  path('teacher/supervisor/mid_term_review/', views.mid_term_review),
                  path('teacher/supervisor/mid_term_review/pass/', views.pass_mid_term),
                  path('teacher/supervisor/translation_review/', views.translation_review),
                  path('teacher/supervisor/weekly_review/', views.weekly_review),
                  path('teacher/supervisor/weekly_review/pass/', views.review_weekly),
                  path('teacher/supervisor/draft_review/', views.draft_review),
                  path('teacher/supervisor/draft_review/pass/', views.review_draft),
                  path('teacher/supervisor/final_review/', views.final_review),
                  path('teacher/supervisor/final_review/pass/', views.review_final),
                  path('teacher/supervisor/project_recommendation/', views.project_recommendation),
                  # 专业毕设负责人模块
                  path('teacher/manager/', views.manager),
                  path('teacher/manager/project_review/', views.project_review),
                  path('teacher/manager/project_review/pass/', views.pass_project),
                  path('teacher/manager/task_review/', views.task_review),
                  path('teacher/manager/task_review/pass_task/', views.pass_task),
                  path('teacher/manager/reviewer_assignment/', views.reviewer_assignment),
                  path('teacher/manager/reviewer_assignment/assign/', views.assign_reviewer),
                  path('teacher/manager/group_assignment/', views.group_assignment),
                  path('teacher/manager/group_assignment/assign/', views.assign_group),
                  path('teacher/manager/group_assignment/assign_student/', views.assign_student),
                  path('teacher/manager/group_assignment/re_assign/', views.reassign_group),
                  # 教学院长模块
                  path('teacher/dean/', views.dean),
                  path('teacher/dean/project_announcement/', views.project_announcement),
                  path('teacher/dean/project_announcement/announce/', views.announce_project),
                  path('teacher/dean/result_announcement/', views.result_announcement),
                  path('teacher/dean/result_announcement/announce/', views.announce_result),
                  path('teacher/dean/announce_result/', views.announce_result),
                  # 教学秘书模块
                  path('teacher/secretary/', views.secretary_index),
                  path('teacher/secretary/thesis_score/', views.thesis_score),
                  path('teacher/secretary/thesis_score/score/', views.score_thesis),
                  path('teacher/secretary/defense_score/', views.defense_score),
                  path('teacher/secretary/defense_score/score/', views.score_defense),
                  path('teacher/secretary/score_announcement/', views.score_announcement),
                  path('teacher/secretary/score_announcement/announce/', views.announce_score),
                  # 管理员模块
                  path('admin/', views.admin),
                  path('admin/information_summary/', views.admin_info),
                  path('admin/user_summary/', views.admin_user),
                  path('admin/command/', views.command),
                  path('admin/command/push/', views.command_push),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
