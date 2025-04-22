from django.urls import path
from api import views

urlpatterns = [
    path('test-suites', views.TestSuiteList.as_view()),
    path('test-suites/<int:pk>', views.TestSuiteDetail.as_view()),
    path('test-suites/<int:pk>/test-cases', views.TestCaseList.as_view()),
    path('test-cases/<int:pk>', views.TestCaseDetail.as_view()),
    path('run-tests', views.TestResult.as_view())
]
