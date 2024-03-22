from django.urls import path
from . import views
from .views import success, signup, signin, staff_signin, deleteitems, updatestock, showorders, addnewitems,updatestatus,completedorders, customerlogout, stafflogout, customerdashboard, download_in_excel, mycart, orderpage


urlpatterns = [
        path('', views.sampling, name='sampling'),
        path('sampling', views.sampling, name='sampling'),
        path('designs', views.designs, name ='designs'),
        path('success', views.success, name='success'),
        path('signup', views.signup, name ='signup'),
        path('signin', views.signin, name='signin'),
        path('customerlogout', views.customerlogout, name='customerlogout'),
        path('stafflogout', views.stafflogout, name='stafflogout'),
        path('verify', views.verify, name='verify'),
        path('check_username_availability', views.check_username_availability, name='check_username_availability'),
        path('staff_signin', views.staff_signin, name='staff_signin'),
        path('sampling_office_dashboard', views.sampling_office_dashboard, name='sampling_office_dashboard'),
        path('showorders', views.showorders, name='showorders'),
        path('updatestock/', views.updatestock, name='updatestock'),
        path('addnewitems', views.addnewitems, name='addnewitems'),
        path('deleteitems', views.deleteitems, name='deleteitems'),
        path('updatestatus/<int:orderno>/', views.updatestatus, name='updatestatus'),
        path('completedorders', views.completedorders, name='completedorders'),
        path('customerdashboard/', views.customerdashboard, name='customerdashboard'),
        path('download/<int:orderno>/', views.download_in_excel, name='download_in_excel'),
        path('mycart', views.mycart, name='mycart'),
        path('orderpage', views.orderpage, name='orderpage'),
        path('get_design_details/<str:design_name>/', views.get_design_details, name='get_design_details'),
    ]
