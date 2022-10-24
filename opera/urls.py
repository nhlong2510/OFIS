from django.urls import path
from . import views


app_name='opera'
urlpatterns = [
    path('folio_create/', views.foliocreate, name="create"),
    path('', views.opera, name="opera"),
    path('api/folio_details/<int:pk>', views.details, name="detail"),
    path('folio_update/<int:pk>', views.folioupdate, name="update"),
    path('folio_adjust/<int:pk>', views.folioadjust, name="adjust"),
    path('api/folio_infos/', views.folioinfo, name="info"),
    path('folio/new/', views.folio_new, name="folio_new"), 
    path('folio/not_upload/', views.folio_upload, name="folio_upload"), 
]