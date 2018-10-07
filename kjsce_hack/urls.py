"""nse_ml URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from hack.views import index, dash2, speech_to_text, login, insert_in_calendar, past_meets, past_meets_details
from django.urls import path

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^app/$', index, name="index"),
    url(r'^dash2/$', dash2, name="dash2"),
    url(r'^dates/$', insert_in_calendar, name="dates"),
    url(r'^s2t/$', speech_to_text, name="speech_to_text"),
    url(r'^past_meets/$', past_meets, name="past_meets"),
    url(r'^past_meets/(?P<id>\d+)/$', past_meets_details, name="past_meets_details"),
    path('', login, name="login"),
    # path('', include(('django.contrib.auth.urls', 'django.contrib.auth'), namespace='auth')),
    # path('', include(('social_django.urls', 'social_django'), namespace='social')),
]
