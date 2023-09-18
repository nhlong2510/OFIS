from django.urls import path
from . import api, views


app_name = 'opera'

urlpatterns = [
    path('', views.opera, name="opera"),
    path('folio/not_upload/', views.folio_upload, name="folio_upload"), 
    path('folio/issued/', views.folio_issue, name="folio_issued"), 
    path('api/folio_create/', api.foliocreate, name="folio_create"),
    path('api/folio_infos/', api.folioinfo, name='folio_infos'),
    path('api/folio_detail/<int:pk>/', api.foliodetail, name='folio_detail'),
    path('api/folio_update/<int:pk>/', api.folioupdate, name='folio_update'),
]
