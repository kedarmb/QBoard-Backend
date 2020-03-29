from django.conf.urls import url
from sprint_1 import views

urlpatterns = [
	url(r'^signup$', views.signup),
    url(r'^login$', views.login),
    url(r'^verify$', views.verify_user),
    url(r'^forgot_password$', views.validate_email),
    url(r'^update_password$', views.update_password),
]
