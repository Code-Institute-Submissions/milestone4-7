from django.conf.urls import url, include
from . import urls_reset
from .views import index, register, profile, logout, login, edit_profile

urlpatterns = [
    url(r'^register/$', register, name='register'),
    url(r'^profile/(?P<pk>\d+)/$', profile, name='profile'),
    url(r'^profile/edit/$', edit_profile, name='edit_profile'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^login/$', login, name='login'),
    url(r'^password-reset/', include(urls_reset)),
]