from django.urls import path
from api import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('test-suites', views.TestSuiteList.as_view()),
    path('test-suites/<int:pk>', views.TestSuiteDetail.as_view()),
    path('test-suites/<int:pk>/test-cases', views.TestCaseList.as_view()),
    path('test-cases/<int:pk>', views.TestCaseDetail.as_view()),
    path('run-tests', views.TestResult.as_view()),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('register/', views.UserCreateView.as_view()),
]
