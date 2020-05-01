from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetView,PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


urlpatterns = [
    url(r'^$',views.home, name = "home"),
    url(r'login/', views.login_user, name = 'login'),
    url(r'^logout/$', views.logout_user, name= "logout"),

    url(r'^register/$', views.register_user, name= "register"),
    url(r'^edit_profile/$', views.edit_profile, name = "edit_profile"),
    url(r'^dashbaord/$', views.dashboard, name = "dashboard"),
    
    #Password Change URL............
    url(r'^change_password/$', views.change_password, name = "change_password"),

    #password Reset URLS...........
    path('password_reset/', PasswordResetView.as_view(), name='password_reset' ),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    #Email Confirm URLs.....
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),

    # My SQL Query URL...
    url(r'^query/$', views.mySQL_view, name="MYSQL"),

    # Saved Query URL
    url(r'^saved-query/$', views.savedQuery_View, name="SavedQuery"),

    # Profile URL
    url(r'^profile/$', views.profile, name="profile"),

    # Create Results Color Range URL
    url(r'^create-color-range/$', views.savedColorRange, name="CreateColorRange"),
    
    
    # Execute Specific Query From DB 1
    path('execute-specific-query-DB/', views.updateDBResults, name="ExecuteDB_Specific_URL"),


    # upDateQueryDB
    path('update-specific-query-DB/', views.upDateQueryDB, name="upDateQueryDB_URL"),
    
    path('view-user-actions',views.UserLogActions, name="UserLogActions_URL"),
    
    path('refresh-query-row/<int:configurationRules_id>/<int:configResultsDataBase_id>/', views.refreshQueryRow, name="refreshQueryRow_URL")
]