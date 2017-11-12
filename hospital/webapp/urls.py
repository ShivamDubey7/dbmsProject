from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$',views.home, name="home"),
    url(r'^admin/$',views.admin,name="admin"),
    url(r'^admin/alterdb$',views.alterdb,name="alterdb"),
    url(r'^admin/alterdb/add',views.add,name="add"),
    url(r'^admin/alterdb/delete',views.delete,name="add"),
    url(r'^login/$',views.login,name="login"),
    url(r'^logout/$',views.logout,name="logout"),
    url(r'^signup/$',views.signup,name="signup"),
    url(r'^team$',views.team,name="team"),
    url(r'^profile/$',views.profile,name="profile"),
    url(r'^appointment/$',views.appointment,name="appointment"),
    url(r'^exp/$',views.exp),
    url(r'^delapp/$',views.delapp, name="delapp"),
    url(r'^contact/$',views.contact,name="contact"),
url(r'^about/$',views.about,name="about"),
url(r'^pay/$',views.pay,name="pay"),
]