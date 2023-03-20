from django.urls import path
from .views import *


urlpatterns = [
    path('', main, name='main'),
    path('del/<int:id>/', deletion_request_pricelist_rec, name='pricelist_rec_del'),
    path('get-dxf/', get_dxf, name='get_dxf'),
    path('convert-dol/', dol_convers_request, name='convert_dol'),
    path('estimate/', estimate, name='estimate'),
    path('estimate/del/', deletion_request_estimate, name='estimate_del'),
    path('estimate/xls/', download_estimate_request, name='estimate_xls'),
    path('estimate/del/<int:id>/', deletion_request_estimate_rec, name='estimate_rec_del'),
]
