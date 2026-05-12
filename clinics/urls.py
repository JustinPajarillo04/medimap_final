from django.urls import path
from . import views


urlpatterns = [
    path("", views.find_clinics_page, name="home"),

    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),

    path("find-clinics/", views.find_clinics_page, name="find_clinics"),
    path("nearby/", views.nearby_page, name="nearby"),
   
    path("admin-management/", views.admin_page, name="admin_page"),
    path("add-clinic/", views.add_clinic, name="add_clinic"),
    path("edit-clinic/<int:clinic_id>/", views.edit_clinic, name="edit_clinic"),
    path("delete-clinic/<int:clinic_id>/", views.delete_clinic, name="delete_clinic"),

    path("api/clinics/", views.clinic_list_api, name="clinic_list_api"),
    path("api/clinics/<int:clinic_id>/", views.clinic_detail_api, name="clinic_detail_api"),
]