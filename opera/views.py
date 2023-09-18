from datetime import date, timedelta
from django.shortcuts import render
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from . models import OfisInfo


@login_required(login_url='user:login')
def opera(request):
    current_day = date.today()
    week = current_day - timedelta(days=7)
    month = current_day - timedelta(days=30)
    folio_created_today = list(OfisInfo.objects.filter(FolioCreatedDate=current_day.strftime('%Y-%m-%d')).values('FolioCreatedDate').annotate(folio_count=Count('id')))[0]['folio_count']
    folio_created_week = list(OfisInfo.objects.filter(Q(FolioCreatedDate__gte=week)&Q(FolioCreatedDate__lte=current_day)).values('FolioCreatedDate').annotate(folio_count=Count('id')))[0]['folio_count']
    folio_created_month = list(OfisInfo.objects.filter(Q(FolioCreatedDate__gte=month)&Q(FolioCreatedDate__lte=current_day)).values('FolioCreatedDate').annotate(folio_count=Count('id')))[0]['folio_count']
    folio_list = [folio_created_today, folio_created_week, folio_created_month]

    folio_issued = list(OfisInfo.objects.filter(EinvoiceInfo__EinvoiceStatus__icontains=0).values('EinvoiceInfo__EinvoiceStatus').annotate(folio_count=Count('id')))[0]
    folio_not_issued = list(OfisInfo.objects.filter(EinvoiceInfo__EinvoiceStatus__icontains=9).values('EinvoiceInfo__EinvoiceStatus').annotate(folio_count=Count('id')))[0]
    folio_status = ["Issued", "Not Upload"]
    folio_count = [folio_issued['folio_count'], folio_not_issued['folio_count']]
     
    return render(request, 'opera/opera.html', {
        "folio_status": folio_status,
        "folio_count": folio_count,
        "folio_list": folio_list,
    })


@login_required(login_url='user:login')
def folio_upload(request):
    documentinfo = OfisInfo.objects.filter(EinvoiceInfo__EinvoiceStatus__icontains='9')
     
    return render(request, 'opera/folio_upload.html', {
        'documentinfo': documentinfo,
    })


@login_required(login_url='user:login')
def folio_issue(request):
    documentinfo = OfisInfo.objects.filter(EinvoiceInfo__EinvoiceStatus__icontains='0')
     
    return render(request, 'opera/folio_issued.html', {
        'documentinfo': documentinfo
    })
