from django.shortcuts import render, redirect
from .services.services import *


def main(request):
    if request.method == 'POST':
        form_price = AddPrice(request.POST)
        if form_price.is_valid():
            form_price.save()
            return redirect('main')
        else:
            print(form_price.errors)
            print(request.POST)
            return redirect('main')

    return render(request, 'main.html', MainServices.get_context_data())


def get_dxf(request):
    return DxfServices.get_dxf()


def deletion_request_pricelist_rec(request, id):
    MainServices.del_pricelist_rec(id=id)
    return redirect('main')


def dol_convers_request(request):
    CurrencyServices.convertto_dol()
    return redirect('main')


def estimate(request):
    if request.method == 'POST':

        if request.POST.get('addestimate'):
            form_estimate = AddEstimate(request.POST)

            if form_estimate.is_valid():
                form_estimate.save()
                return redirect('estimate')

        if request.POST.get('adddxf'):
            dxf_req = request.FILES['dxf_scheme']
            DxfServices.collect_estimate(dxf_req=dxf_req)
            return redirect('estimate')

    return render(request, 'estimate.html', EstimateServices.get_context_data())


def download_estimate_request(request):
    return XlsServices.get_estimate()


def deletion_request_estimate_rec(request, id):
    EstimateServices.del_estimate_rec(id)
    return redirect('estimate')


def deletion_request_estimate(request):
    EstimateServices.del_estimate()
    return redirect('estimate')


