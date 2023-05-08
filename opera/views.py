from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from . models import FlipInfo
from . serialize import FlipSerialize
from . pagination import MyPagination
from rest_framework import status, viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.contrib.auth.decorators import login_required
import math
from django.db.models import Q


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def foliocreate(request):
    post_data = request.data
    # if service charge is not set as tax type, then will have to recalculate the NetAmount
    # if len(post_data["FolioInfo"]["RevenueBucketInfo"]) == 3:
    #     new_info = FlipInfo.objects.create(
    #         DocumentInfo = post_data["DocumentInfo"],
    #         FiscalTerminalInfo = post_data["FiscalTerminalInfo"],
    #         FolioInfo = post_data["FolioInfo"],
    #         HotelInfo = post_data["HotelInfo"],
    #         ReservationInfo = post_data["ReservationInfo"],
    #         FiscalFolioUserInfo = post_data["FiscalFolioUserInfo"],
    #         BusinessDate = post_data["DocumentInfo"]["BusinessDate"],
    #         BusinessDateTime = post_data["DocumentInfo"]["BusinessDateTime"],
    #         FolioNo = post_data["DocumentInfo"]["BillNo"],
    #         NetAmount = post_data["FolioInfo"]["TotalInfo"]["GrossAmount"] - post_data["FolioInfo"]["RevenueBucketInfo"][1]["BucketCodeTotalGross"] - post_data["FolioInfo"]["RevenueBucketInfo"][2]["BucketCodeTotalGross"]
    #     )
    # elif len(post_data["FolioInfo"]["RevenueBucketInfo"]) > 3:
    #     new_info = FlipInfo.objects.create(
    #         DocumentInfo = post_data["DocumentInfo"],
    #         FiscalTerminalInfo = post_data["FiscalTerminalInfo"],
    #         FolioInfo = post_data["FolioInfo"],
    #         HotelInfo = post_data["HotelInfo"],
    #         ReservationInfo = post_data["ReservationInfo"],
    #         FiscalFolioUserInfo = post_data["FiscalFolioUserInfo"],
    #         BusinessDate = post_data["DocumentInfo"]["BusinessDate"],
    #         BusinessDateTime = post_data["DocumentInfo"]["BusinessDateTime"],
    #         FolioNo = post_data["DocumentInfo"]["BillNo"],
    #         NetAmount = post_data["FolioInfo"]["TotalInfo"]["GrossAmount"] - post_data["FolioInfo"]["RevenueBucketInfo"][1]["BucketCodeTotalGross"] - post_data["FolioInfo"]["RevenueBucketInfo"][2]["BucketCodeTotalGross"] - post_data["FolioInfo"]["RevenueBucketInfo"][3]["BucketCodeTotalGross"]
    #     )
    # else:
    new_info = FlipInfo.objects.create(
        DocumentInfo = post_data["DocumentInfo"],
        FiscalTerminalInfo = post_data["FiscalTerminalInfo"],
        FolioInfo = post_data["FolioInfo"],
        HotelInfo = post_data["HotelInfo"],
        ReservationInfo = post_data["ReservationInfo"],
        FiscalFolioUserInfo = post_data["FiscalFolioUserInfo"],
        BusinessDate = post_data["DocumentInfo"]["BusinessDate"],
        BusinessDateTime = post_data["DocumentInfo"]["BusinessDateTime"],
        FolioNo = post_data["DocumentInfo"]["BillNo"],
        NetAmount = post_data["FolioInfo"]["TotalInfo"]["NetAmount"]
    )
    new_info.save()

    message_status = {
        "FiscalFolioNo": post_data["DocumentInfo"]["FiscalFolioId"],
        "FiscalBillGenerationDateTime": post_data["DocumentInfo"]["BusinessDateTime"],
        "FiscalOutput": {
            "Name": "DATA_TO_EINVOICE",
            "Value": "OperaWillTransformThisDatatoEInvoice"
        },
            "StatusMessage": {
                "Message": {
                    "Description": "Folio is posted, successful response",
                    "Type": "COMPLETED"
                }
            }
        }
    # return Response(message_status, status=status.HTTP_200_OK, content_type='application/json')
    return JsonResponse(message_status, safe=False)


@login_required(login_url='user:login')
def opera(request):
    documentinfo = FlipInfo.objects.all()
    documentadjust = FlipInfo.objects.filter(Q(EinvoiceStatus__icontains=9)&Q(NetAmount__lte=0))
    documentupload = FlipInfo.objects.filter(Q(EinvoiceStatus__icontains=9))
    documentdraft = FlipInfo.objects.filter(Q(EinvoiceStatus__icontains=0))
    documentissued = FlipInfo.objects.filter(Q(EinvoiceStatus__icontains=1))
     
    return render(request, 'opera/opera.html', {
        'documentinfo': documentinfo,
        'documentadjust': documentadjust,
        'documentdraft': documentdraft,
        'documentissued': documentissued,
        'documentupload': documentupload,
    })


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def folioinfo(request):
    status = request.GET.get('status')
    fdate = request.GET.get('fdate')
    tdate = request.GET.get('tdate')
    folio = request.GET.get('folio')
    # page = int(request.GET.get('page', 1))
    # per_page=1
    docobj = FlipInfo.objects.all().order_by('-id')

    if status:
        docobj = FlipInfo.objects.filter(EinvoiceStatus__icontains=status).order_by('-id')
    
    if status and fdate and tdate:
        docobj = FlipInfo.objects.filter(Q(EinvoiceStatus__icontains=status)&Q(BusinessDate__icontains=fdate)&Q(BusinessDate__icontains=tdate)).order_by('-id')
    
    if status and fdate and tdate and folio:
        docobj = FlipInfo.objects.filter(Q(EinvoiceStatus__icontains=status)&Q(BusinessDate__icontains=fdate)&Q(BusinessDate__icontains=tdate)&Q(FolioNo=folio)).order_by('-id')

    if status and folio:
        docobj = FlipInfo.objects.filter(Q(EinvoiceStatus__icontains=status)&Q(FolioNo=folio)).order_by('-id')
    
    if folio:
        docobj = FlipInfo.objects.filter(FolioNo=folio)
    # flipdata = list(docobj.values())
    # total = docobj.count()
    # start = (page - 1) * per_page
    # end = page * per_page

    # flip_data = FlipSerialize(flipdata[start:end], many=True).data

    flipdata = list(docobj.values())
    paginator = MyPagination()
    page = paginator.paginate_queryset(flipdata, request)
    flip_data = FlipSerialize(page, many=True).data

    flipinfo = []
    for flip in flip_data:
        if flip["FolioInfo"]["PayeeInfo"]["NameType"] == "INDIVIDUAL" and "Address4" in flip["FolioInfo"]["PayeeInfo"]["Address"] and "Email" in flip["ReservationInfo"]["GuestInfo"]:
            flip_info = {
            "id": flip["id"],
            "EinvoiceInfo": {
                "EinvoiceNumber": flip["EinvoiceNumber"],
                "EinvoiceType": flip["EinvoiceType"],
                "EinvoiceStatus": flip["EinvoiceStatus"],
                "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                "EinvoiceFKey": flip["EinvoiceFKey"],
                "EinvoicePattern": flip["EinvoicePattern"],
                "EinvoiceSerial": "C23MAB",
                "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"],
            },
            "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
            "Arrival": flip["ReservationInfo"]["ArrivalDate"],
            "Departure": flip["ReservationInfo"]["DepartureDate"],
            "GuestInfo": {
                "Email": flip["ReservationInfo"]["GuestInfo"].get("Email", ' '),
                "Phone": flip["ReservationInfo"]["GuestInfo"].get("Phone", ' '),
                "Name": flip["ReservationInfo"]["GuestInfo"].get("LastName",' ') + ' ' + flip["ReservationInfo"]["GuestInfo"].get("FirstName",' '),
                "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                },
            "HotelCode": flip["HotelInfo"]["HotelCode"],
            "HotelName": flip["HotelInfo"]["HotelName"],
            "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
            "FolioNo": flip["FolioNo"],
            "FolioCreatedDate": flip["BusinessDate"],
            "FolioCreatedDateTime": flip["BusinessDateTime"],
            "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
            "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
            "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Address"]["Address1"],
            "VATNo": flip["FolioInfo"]["PayeeInfo"]["Address"]["Address4"],
            "PayeeAddress": {
                "Address2" : flip["FolioInfo"]["PayeeInfo"]["Address"]["Address2"],
                "Address3" : flip["FolioInfo"]["PayeeInfo"]["Address"]["Address3"],
            },
            "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
            "NetAmount": flip["NetAmount"],
            "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
            "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
            "Postings": flip["FolioInfo"]["Postings"],
            "TrxInfo": flip["FolioInfo"]["TrxInfo"]
            }
            flipinfo.append(flip_info)

        elif flip["FolioInfo"]["PayeeInfo"]["NameType"] == "INDIVIDUAL" and "Address4" in flip["FolioInfo"]["PayeeInfo"]["Address"] and "Email" not in flip["ReservationInfo"]["GuestInfo"]:
            flip_info = {
            "id": flip["id"],
            "EinvoiceInfo": {
                "EinvoiceNumber": flip["EinvoiceNumber"],
                "EinvoiceType": flip["EinvoiceType"],
                "EinvoiceStatus": flip["EinvoiceStatus"],
                "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                "EinvoiceFKey": flip["EinvoiceFKey"],
                "EinvoicePattern": flip["EinvoicePattern"],
                "EinvoiceSerial": "C23MAB",
                "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
            },
            "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
            "Arrival": flip["ReservationInfo"]["ArrivalDate"],
            "Departure": flip["ReservationInfo"]["DepartureDate"],
            "GuestInfo": {
                "Email": " ",
                "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                },
            "HotelCode": flip["HotelInfo"]["HotelCode"],
            "HotelName": flip["HotelInfo"]["HotelName"],
            "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
            "FolioNo": flip["FolioNo"],
            "FolioCreatedDate": flip["BusinessDate"],
            "FolioCreatedDateTime": flip["BusinessDateTime"],
            "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
            "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
            "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Address"]["Address1"],
            "VATNo": flip["FolioInfo"]["PayeeInfo"]["Address"]["Address4"],
            "PayeeAddress": {
                "Address2" : flip["FolioInfo"]["PayeeInfo"]["Address"]["Address2"],
                "Address3" : flip["FolioInfo"]["PayeeInfo"]["Address"]["Address3"],
            },
            "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
            "NetAmount": flip["NetAmount"],
            "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
            "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
            "Postings": flip["FolioInfo"]["Postings"],
            "TrxInfo": flip["FolioInfo"]["TrxInfo"]
            }
            flipinfo.append(flip_info)

        elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name2" in flip["FolioInfo"]["PayeeInfo"] and "Email" in flip["ReservationInfo"]["GuestInfo"]:
            flip_info = {
                "id": flip["id"],
                "EinvoiceInfo": {
                    "EinvoiceNumber": flip["EinvoiceNumber"],
                    "EinvoiceType": flip["EinvoiceType"],
                    "EinvoiceStatus": flip["EinvoiceStatus"],
                    "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                    "EinvoiceFKey": flip["EinvoiceFKey"],
                    "EinvoicePattern": flip["EinvoicePattern"],
                    "EinvoiceSerial": "C23MAB",
                    "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                    "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
                },
                "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
                "Arrival": flip["ReservationInfo"]["ArrivalDate"],
                "Departure": flip["ReservationInfo"]["DepartureDate"],
                "GuestInfo": {
                    "Email": flip["ReservationInfo"]["GuestInfo"]["Email"],
                    "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                    "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                    "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                    },
                "HotelCode": flip["HotelInfo"]["HotelCode"],
                "HotelName": flip["HotelInfo"]["HotelName"],
                "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
                "FolioNo": flip["FolioNo"],
                "FolioCreatedDate": flip["BusinessDate"],
                "FolioCreatedDateTime": flip["BusinessDateTime"],
                "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
                "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
                "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Name2"],
                "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
                "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
                "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
                "NetAmount": flip["NetAmount"],
                "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
                "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
                "Postings": flip["FolioInfo"]["Postings"],
                "TrxInfo": flip["FolioInfo"]["TrxInfo"]
            }
            flipinfo.append(flip_info)

        elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name2" in flip["FolioInfo"]["PayeeInfo"] and "Email" not in flip["ReservationInfo"]["GuestInfo"]:
            flip_info = {
                "id": flip["id"],
                "EinvoiceInfo": {
                    "EinvoiceNumber": flip["EinvoiceNumber"],
                    "EinvoiceType": flip["EinvoiceType"],
                    "EinvoiceStatus": flip["EinvoiceStatus"],
                    "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                    "EinvoiceFKey": flip["EinvoiceFKey"],
                    "EinvoicePattern": flip["EinvoicePattern"],
                    "EinvoiceSerial": "C23MAB",
                    "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                    "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
                },
                "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
                "Arrival": flip["ReservationInfo"]["ArrivalDate"],
                "Departure": flip["ReservationInfo"]["DepartureDate"],
                "GuestInfo": {
                    "Email": {},
                    "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                    "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"],
                    "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                    },
                "HotelCode": flip["HotelInfo"]["HotelCode"],
                "HotelName": flip["HotelInfo"]["HotelName"],
                "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
                "FolioNo": flip["FolioNo"],
                "FolioCreatedDate": flip["BusinessDate"],
                "FolioCreatedDateTime": flip["BusinessDateTime"],
                "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
                "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
                "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Name2"],
                "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
                "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
                "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
                "NetAmount": flip["NetAmount"],
                "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
                "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
                "Postings": flip["FolioInfo"]["Postings"],
                "TrxInfo": flip["FolioInfo"]["TrxInfo"]
            }
            flipinfo.append(flip_info)

        elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name2" not in flip["FolioInfo"]["PayeeInfo"] and "Email" not in flip["ReservationInfo"]["GuestInfo"]:
            flip_info = {
                "id": flip["id"],
                "EinvoiceInfo": {
                    "EinvoiceNumber": flip["EinvoiceNumber"],
                    "EinvoiceType": flip["EinvoiceType"],
                    "EinvoiceStatus": flip["EinvoiceStatus"],
                    "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                    "EinvoiceFKey": flip["EinvoiceFKey"],
                    "EinvoicePattern": flip["EinvoicePattern"],
                    "EinvoiceSerial": "C23MAB",
                    "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                    "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
                },
                "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
                "Arrival": flip["ReservationInfo"]["ArrivalDate"],
                "Departure": flip["ReservationInfo"]["DepartureDate"],
                "GuestInfo": {
                    "Email": " ",
                    "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                    "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                    "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                    },
                "HotelCode": flip["HotelInfo"]["HotelCode"],
                "HotelName": flip["HotelInfo"]["HotelName"],
                "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
                "FolioNo": flip["FolioNo"],
                "FolioCreatedDate": flip["BusinessDate"],
                "FolioCreatedDateTime": flip["BusinessDateTime"],
                "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
                "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
                "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["LastName"],
                "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
                "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
                "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
                "NetAmount": flip["NetAmount"],
                "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
                "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
                "Postings": flip["FolioInfo"]["Postings"],
                "TrxInfo": flip["FolioInfo"]["TrxInfo"]
            }
            flipinfo.append(flip_info)
        
        elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name2" not in flip["FolioInfo"]["PayeeInfo"] and "Email" in flip["ReservationInfo"]["GuestInfo"]:
            flip_info = {
                "id": flip["id"],
                "EinvoiceInfo": {
                    "EinvoiceNumber": flip["EinvoiceNumber"],
                    "EinvoiceType": flip["EinvoiceType"],
                    "EinvoiceStatus": flip["EinvoiceStatus"],
                    "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                    "EinvoiceFKey": flip["EinvoiceFKey"],
                    "EinvoicePattern": flip["EinvoicePattern"],
                    "EinvoiceSerial": "C23MAB",
                    "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                    "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
                },
                "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
                "Arrival": flip["ReservationInfo"]["ArrivalDate"],
                "Departure": flip["ReservationInfo"]["DepartureDate"],
                "GuestInfo": {
                    "Email": flip["ReservationInfo"]["GuestInfo"]["Email"],
                    "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                    "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                    "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                    },
                "HotelCode": flip["HotelInfo"]["HotelCode"],
                "HotelName": flip["HotelInfo"]["HotelName"],
                "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
                "FolioNo": flip["FolioNo"],
                "FolioCreatedDate": flip["BusinessDate"],
                "FolioCreatedDateTime": flip["BusinessDateTime"],
                "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
                "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
                "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["LastName"],
                "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
                "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
                "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
                "NetAmount": flip["NetAmount"],
                "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
                "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
                "Postings": flip["FolioInfo"]["Postings"],
                "TrxInfo": flip["FolioInfo"]["TrxInfo"]
            }
            flipinfo.append(flip_info)
        
        elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name3" in flip["FolioInfo"]["PayeeInfo"] and "Email" in flip["ReservationInfo"]["GuestInfo"]:
            flip_info = {
                "id": flip["id"],
                "EinvoiceInfo": {
                    "EinvoiceNumber": flip["EinvoiceNumber"],
                    "EinvoiceType": flip["EinvoiceType"],
                    "EinvoiceStatus": flip["EinvoiceStatus"],
                    "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                    "EinvoiceFKey": flip["EinvoiceFKey"],
                    "EinvoicePattern": flip["EinvoicePattern"],
                    "EinvoiceSerial": "C23MAB",
                    "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                    "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
                },
                "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
                "Arrival": flip["ReservationInfo"]["ArrivalDate"],
                "Departure": flip["ReservationInfo"]["DepartureDate"],
                "GuestInfo": {
                    "Email": flip["ReservationInfo"]["GuestInfo"]["Email"],
                    "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                    "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                    "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                    },
                "HotelCode": flip["HotelInfo"]["HotelCode"],
                "HotelName": flip["HotelInfo"]["HotelName"],
                "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
                "FolioNo": flip["FolioNo"],
                "FolioCreatedDate": flip["BusinessDate"],
                "FolioCreatedDateTime": flip["BusinessDateTime"],
                "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
                "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
                "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Name2"]+' '+flip["FolioInfo"]["PayeeInfo"]["Name3"],
                "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
                "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
                "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
                "NetAmount": flip["NetAmount"],
                "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
                "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
                "Postings": flip["FolioInfo"]["Postings"],
                "TrxInfo": flip["FolioInfo"]["TrxInfo"]
            }
            flipinfo.append(flip_info)
        
        elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name3" in flip["FolioInfo"]["PayeeInfo"] and "Email" not in flip["ReservationInfo"]["GuestInfo"]:
            flip_info = {
                "id": flip["id"],
                "EinvoiceInfo": {
                    "EinvoiceNumber": flip["EinvoiceNumber"],
                    "EinvoiceType": flip["EinvoiceType"],
                    "EinvoiceStatus": flip["EinvoiceStatus"],
                    "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                    "EinvoiceFKey": flip["EinvoiceFKey"],
                    "EinvoicePattern": flip["EinvoicePattern"],
                    "EinvoiceSerial": "C23MAB",
                    "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                    "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
                },
                "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
                "Arrival": flip["ReservationInfo"]["ArrivalDate"],
                "Departure": flip["ReservationInfo"]["DepartureDate"],
                "GuestInfo": {
                    "Email": " ",
                    "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                    "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                    "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                    },
                "HotelCode": flip["HotelInfo"]["HotelCode"],
                "HotelName": flip["HotelInfo"]["HotelName"],
                "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
                "FolioNo": flip["FolioNo"],
                "FolioCreatedDate": flip["BusinessDate"],
                "FolioCreatedDateTime": flip["BusinessDateTime"],
                "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
                "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
                "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Name2"]+' '+flip["FolioInfo"]["PayeeInfo"]["Name3"],
                "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
                "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
                "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
                "NetAmount": flip["NetAmount"],
                "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
                "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
                "Postings": flip["FolioInfo"]["Postings"],
                "TrxInfo": flip["FolioInfo"]["TrxInfo"]
            }
            flipinfo.append(flip_info)

        else:
            flip_info = {
                "id": flip["id"],
                "EinvoiceInfo": {
                    "EinvoiceNumber": flip["EinvoiceNumber"],
                    "EinvoiceType": flip["EinvoiceType"],
                    "EinvoiceStatus": flip["EinvoiceStatus"],
                    "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                    "EinvoiceFKey": flip["EinvoiceFKey"],
                    "EinvoicePattern": flip["EinvoicePattern"],
                    "EinvoiceSerial": "C23MAB",
                    "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                    "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
                },
                "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
                "Arrival": flip["ReservationInfo"]["ArrivalDate"],
                "Departure": flip["ReservationInfo"]["DepartureDate"],
                "GuestInfo": flip["ReservationInfo"]["GuestInfo"],
                "HotelCode": flip["HotelInfo"]["HotelCode"],
                "HotelName": flip["HotelInfo"]["HotelName"],
                "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
                "FolioNo": flip["FolioNo"],
                "FolioCreatedDate": flip["BusinessDate"],
                "FolioCreatedDateTime": flip["BusinessDateTime"],
                "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
                "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
                "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["LastName"],
                "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
                "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
                "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
                "NetAmount": flip["NetAmount"],
                "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
                "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
                "Postings": flip["FolioInfo"]["Postings"],
                "TrxInfo": flip["FolioInfo"]["TrxInfo"]
            }
            flipinfo.append(flip_info)
    
    return paginator.get_paginated_response(flipinfo)


@login_required(login_url='user:login')
def folio_new(request):
    documentinfo = list(FlipInfo.objects.filter(EinvoiceStatus__icontains='0').values())
     
    return render(request, 'opera/folio_new.html', {
        'documentinfo': documentinfo
    })


@login_required(login_url='user:login')
def folio_upload(request):
    documentinfo = list(FlipInfo.objects.filter(EinvoiceStatus__icontains='9').values())
    documentadjust = list(FlipInfo.objects.filter(Q(EinvoiceStatus__icontains='9')&Q(NetAmount__lte=0)).values())
     
    return render(request, 'opera/folio_upload.html', {
        'documentinfo': documentinfo,
        'documentadjust': documentadjust
    })


@login_required(login_url='user:login')
def folio_issue(request):
    documentinfo = list(FlipInfo.objects.filter(EinvoiceStatus__icontains='1').values())
     
    return render(request, 'opera/folio_issued.html', {
        'documentinfo': documentinfo
    })


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def details(request, pk):
    docinfo = FlipInfo.objects.filter(id=pk)
    flip = list(docinfo.values())[0]
    if flip["FolioInfo"]["PayeeInfo"]["NameType"] == "INDIVIDUAL" and "Address4" in flip["FolioInfo"]["PayeeInfo"]["Address"] and "Email" in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
        "id": pk,
        "EinvoiceInfo": {
            "EinvoiceNumber": flip["EinvoiceNumber"],
            "EinvoiceType": flip["EinvoiceType"],
            "EinvoiceStatus": flip["EinvoiceStatus"],
            "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
            "EinvoiceFKey": flip["EinvoiceFKey"],
            "EinvoicePattern": flip["EinvoicePattern"],
            "EinvoiceSerial": "C23MAB",
            "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
            "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"],
        },
        "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
        "Arrival": flip["ReservationInfo"]["ArrivalDate"],
        "Departure": flip["ReservationInfo"]["DepartureDate"],
        "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
        "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
        "GuestInfo": {
            "Email": flip["ReservationInfo"]["GuestInfo"]["Email"],
            "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
            "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"] + ' ' + flip["ReservationInfo"]["GuestInfo"]["FirstName"],
            "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
            },
        "HotelCode": flip["HotelInfo"]["HotelCode"],
        "HotelName": flip["HotelInfo"]["HotelName"],
        "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
        "FolioNo": flip["FolioNo"],
        "FolioCreatedDate": flip["BusinessDate"],
        "FolioCreatedDateTime": flip["BusinessDateTime"],
        "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
        "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
        "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Address"]["Address1"],
        "VATNo": flip["FolioInfo"]["PayeeInfo"]["Address"]["Address4"],
        "PayeeAddress": {
            "Address2" : flip["FolioInfo"]["PayeeInfo"]["Address"]["Address2"],
            "Address3" : flip["FolioInfo"]["PayeeInfo"]["Address"]["Address3"],
        },
        "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
        "NetAmount": flip["NetAmount"],
        "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
        "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
        "Postings": flip["FolioInfo"]["Postings"],
        "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }

    elif flip["FolioInfo"]["PayeeInfo"]["NameType"] == "INDIVIDUAL" and "Address4" in flip["FolioInfo"]["PayeeInfo"]["Address"] and "Email" not in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
        "id": pk,
        "EinvoiceInfo": {
            "EinvoiceNumber": flip["EinvoiceNumber"],
            "EinvoiceType": flip["EinvoiceType"],
            "EinvoiceStatus": flip["EinvoiceStatus"],
            "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
            "EinvoiceFKey": flip["EinvoiceFKey"],
            "EinvoicePattern": flip["EinvoicePattern"],
            "EinvoiceSerial": "C23MAB",
            "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
            "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
        },
        "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
        "Arrival": flip["ReservationInfo"]["ArrivalDate"],
        "Departure": flip["ReservationInfo"]["DepartureDate"],
        "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
        "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
        "GuestInfo": {
            "Email": {},
            "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
            "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
            "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
            },
        "HotelCode": flip["HotelInfo"]["HotelCode"],
        "HotelName": flip["HotelInfo"]["HotelName"],
        "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
        "FolioNo": flip["FolioNo"],
        "FolioCreatedDate": flip["BusinessDate"],
        "FolioCreatedDateTime": flip["BusinessDateTime"],
        "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
        "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
        "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Address"]["Address1"],
        "VATNo": flip["FolioInfo"]["PayeeInfo"]["Address"]["Address4"],
        "PayeeAddress": {
            "Address2" : flip["FolioInfo"]["PayeeInfo"]["Address"]["Address2"],
            "Address3" : flip["FolioInfo"]["PayeeInfo"]["Address"]["Address3"],
        },
        "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
        "NetAmount": flip["NetAmount"],
        "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
        "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
        "Postings": flip["FolioInfo"]["Postings"],
        "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }

    elif flip["FolioInfo"]["PayeeInfo"]["NameType"] == "INDIVIDUAL" and "Address4" not in flip["FolioInfo"]["PayeeInfo"]["Address"] and "Email" not in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
        "id": pk,
        "EinvoiceInfo": {
            "EinvoiceNumber": flip["EinvoiceNumber"],
            "EinvoiceType": flip["EinvoiceType"],
            "EinvoiceStatus": flip["EinvoiceStatus"],
            "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
            "EinvoiceFKey": flip["EinvoiceFKey"],
            "EinvoicePattern": flip["EinvoicePattern"],
            "EinvoiceSerial": "C23MAB",
            "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
            "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
        },
        "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
        "Arrival": flip["ReservationInfo"]["ArrivalDate"],
        "Departure": flip["ReservationInfo"]["DepartureDate"],
        "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
        "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
        "GuestInfo": {
            "Email": {},
            "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
            "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
            "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
            },
        "HotelCode": flip["HotelInfo"]["HotelCode"],
        "HotelName": flip["HotelInfo"]["HotelName"],
        "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
        "FolioNo": flip["FolioNo"],
        "FolioCreatedDate": flip["BusinessDate"],
        "FolioCreatedDateTime": flip["BusinessDateTime"],
        "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
        "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
        "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["LastName"]+' '+flip["FolioInfo"]["PayeeInfo"]["FirstName"],
        "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
        "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
        "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
        "NetAmount": flip["NetAmount"],
        "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
        "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
        "Postings": flip["FolioInfo"]["Postings"],
        "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }
    
    elif flip["FolioInfo"]["PayeeInfo"]["NameType"] == "INDIVIDUAL" and "Address4" not in flip["FolioInfo"]["PayeeInfo"]["Address"] and "Email" in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
        "id": pk,
        "EinvoiceInfo": {
            "EinvoiceNumber": flip["EinvoiceNumber"],
            "EinvoiceType": flip["EinvoiceType"],
            "EinvoiceStatus": flip["EinvoiceStatus"],
            "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
            "EinvoiceFKey": flip["EinvoiceFKey"],
            "EinvoicePattern": flip["EinvoicePattern"],
            "EinvoiceSerial": "C23MAB",
            "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
            "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
        },
        "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
        "Arrival": flip["ReservationInfo"]["ArrivalDate"],
        "Departure": flip["ReservationInfo"]["DepartureDate"],
        "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
        "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
        "GuestInfo": {
            "Email": flip["ReservationInfo"]["GuestInfo"]["Email"],
            "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
            "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
            "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
            },
        "HotelCode": flip["HotelInfo"]["HotelCode"],
        "HotelName": flip["HotelInfo"]["HotelName"],
        "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
        "FolioNo": flip["FolioNo"],
        "FolioCreatedDate": flip["BusinessDate"],
        "FolioCreatedDateTime": flip["BusinessDateTime"],
        "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
        "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
        "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["LastName"]+' '+flip["FolioInfo"]["PayeeInfo"]["FirstName"],
        "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
        "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
        "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
        "NetAmount": flip["NetAmount"],
        "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
        "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
        "Postings": flip["FolioInfo"]["Postings"],
        "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }

    elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name2" in flip["FolioInfo"]["PayeeInfo"] and "Email" in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
            "id": pk,
            "EinvoiceInfo": {
                "EinvoiceNumber": flip["EinvoiceNumber"],
                "EinvoiceType": flip["EinvoiceType"],
                "EinvoiceStatus": flip["EinvoiceStatus"],
                "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                "EinvoiceFKey": flip["EinvoiceFKey"],
                "EinvoicePattern": flip["EinvoicePattern"],
                "EinvoiceSerial": "C23MAB",
                "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
            },
            "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
            "Arrival": flip["ReservationInfo"]["ArrivalDate"],
            "Departure": flip["ReservationInfo"]["DepartureDate"],
            "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
            "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
            "GuestInfo": {
                "Email": flip["ReservationInfo"]["GuestInfo"]["Email"],
                "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                },
            "HotelCode": flip["HotelInfo"]["HotelCode"],
            "HotelName": flip["HotelInfo"]["HotelName"],
            "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
            "FolioNo": flip["FolioNo"],
            "FolioCreatedDate": flip["BusinessDate"],
            "FolioCreatedDateTime": flip["BusinessDateTime"],
            "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
            "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
            "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Name2"],
            "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
            "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
            "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
            "NetAmount": flip["NetAmount"],
            "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
            "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
            "Postings": flip["FolioInfo"]["Postings"],
            "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }

    elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name2" in flip["FolioInfo"]["PayeeInfo"] and "Email" not in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
            "id": pk,
            "EinvoiceInfo": {
                "EinvoiceNumber": flip["EinvoiceNumber"],
                "EinvoiceType": flip["EinvoiceType"],
                "EinvoiceStatus": flip["EinvoiceStatus"],
                "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                "EinvoiceFKey": flip["EinvoiceFKey"],
                "EinvoicePattern": flip["EinvoicePattern"],
                "EinvoiceSerial": "C23MAB",
                "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
            },
            "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
            "Arrival": flip["ReservationInfo"]["ArrivalDate"],
            "Departure": flip["ReservationInfo"]["DepartureDate"],
            "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
            "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
            "GuestInfo": {
                "Email": {},
                "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"],
                "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                },
            "HotelCode": flip["HotelInfo"]["HotelCode"],
            "HotelName": flip["HotelInfo"]["HotelName"],
            "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
            "FolioNo": flip["FolioNo"],
            "FolioCreatedDate": flip["BusinessDate"],
            "FolioCreatedDateTime": flip["BusinessDateTime"],
            "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
            "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
            "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Name2"],
            "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
            "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
            "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
            "NetAmount": flip["NetAmount"],
            "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
            "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
            "Postings": flip["FolioInfo"]["Postings"],
            "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }

    elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name2" not in flip["FolioInfo"]["PayeeInfo"] and "Email" not in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
            "id": pk,
            "EinvoiceInfo": {
                "EinvoiceNumber": flip["EinvoiceNumber"],
                "EinvoiceType": flip["EinvoiceType"],
                "EinvoiceStatus": flip["EinvoiceStatus"],
                "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                "EinvoiceFKey": flip["EinvoiceFKey"],
                "EinvoicePattern": flip["EinvoicePattern"],
                "EinvoiceSerial": "C23MAB",
                "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
            },
            "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
            "Arrival": flip["ReservationInfo"]["ArrivalDate"],
            "Departure": flip["ReservationInfo"]["DepartureDate"],
            "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
            "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
            "GuestInfo": {
                "Email": {},
                "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                },
            "HotelCode": flip["HotelInfo"]["HotelCode"],
            "HotelName": flip["HotelInfo"]["HotelName"],
            "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
            "FolioNo": flip["FolioNo"],
            "FolioCreatedDate": flip["BusinessDate"],
            "FolioCreatedDateTime": flip["BusinessDateTime"],
            "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
            "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
            "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["LastName"],
            "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
            "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
            "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
            "NetAmount": flip["NetAmount"],
            "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
            "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
            "Postings": flip["FolioInfo"]["Postings"],
            "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }
    
    elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name2" not in flip["FolioInfo"]["PayeeInfo"] and "Email" in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
            "id": pk,
            "EinvoiceInfo": {
                "EinvoiceNumber": flip["EinvoiceNumber"],
                "EinvoiceType": flip["EinvoiceType"],
                "EinvoiceStatus": flip["EinvoiceStatus"],
                "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                "EinvoiceFKey": flip["EinvoiceFKey"],
                "EinvoicePattern": flip["EinvoicePattern"],
                "EinvoiceSerial": "C23MAB",
                "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
            },
            "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
            "Arrival": flip["ReservationInfo"]["ArrivalDate"],
            "Departure": flip["ReservationInfo"]["DepartureDate"],
            "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
            "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
            "GuestInfo": {
                "Email": flip["ReservationInfo"]["GuestInfo"]["Email"],
                "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                },
            "HotelCode": flip["HotelInfo"]["HotelCode"],
            "HotelName": flip["HotelInfo"]["HotelName"],
            "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
            "FolioNo": flip["FolioNo"],
            "FolioCreatedDate": flip["BusinessDate"],
            "FolioCreatedDateTime": flip["BusinessDateTime"],
            "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
            "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
            "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["LastName"],
            "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
            "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
            "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
            "NetAmount": flip["NetAmount"],
            "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
            "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
            "Postings": flip["FolioInfo"]["Postings"],
            "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }
    
    elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name3" in flip["FolioInfo"]["PayeeInfo"] and "Email" in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
            "id": pk,
            "EinvoiceInfo": {
                "EinvoiceNumber": flip["EinvoiceNumber"],
                "EinvoiceType": flip["EinvoiceType"],
                "EinvoiceStatus": flip["EinvoiceStatus"],
                "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                "EinvoiceFKey": flip["EinvoiceFKey"],
                "EinvoicePattern": flip["EinvoicePattern"],
                "EinvoiceSerial": "C23MAB",
                "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
            },
            "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
            "Arrival": flip["ReservationInfo"]["ArrivalDate"],
            "Departure": flip["ReservationInfo"]["DepartureDate"],
            "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
            "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
            "GuestInfo": {
                "Email": flip["ReservationInfo"]["GuestInfo"]["Email"],
                "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                },
            "HotelCode": flip["HotelInfo"]["HotelCode"],
            "HotelName": flip["HotelInfo"]["HotelName"],
            "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
            "FolioNo": flip["FolioNo"],
            "FolioCreatedDate": flip["BusinessDate"],
            "FolioCreatedDateTime": flip["BusinessDateTime"],
            "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
            "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
            "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Name2"]+' '+flip["FolioInfo"]["PayeeInfo"]["Name3"],
            "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
            "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
            "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
            "NetAmount": flip["NetAmount"],
            "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
            "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
            "Postings": flip["FolioInfo"]["Postings"],
            "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }
    
    elif flip["FolioInfo"]["PayeeInfo"]["NameType"] != "INDIVIDUAL" and "Name3" in flip["FolioInfo"]["PayeeInfo"] and "Email" not in flip["ReservationInfo"]["GuestInfo"]:
        flip_info = {
            "id": pk,
            "EinvoiceInfo": {
                "EinvoiceNumber": flip["EinvoiceNumber"],
                "EinvoiceType": flip["EinvoiceType"],
                "EinvoiceStatus": flip["EinvoiceStatus"],
                "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                "EinvoiceFKey": flip["EinvoiceFKey"],
                "EinvoicePattern": flip["EinvoicePattern"],
                "EinvoiceSerial": "C23MAB",
                "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
            },
            "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
            "Arrival": flip["ReservationInfo"]["ArrivalDate"],
            "Departure": flip["ReservationInfo"]["DepartureDate"],
            "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
            "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
            "GuestInfo": {
                "Email": {},
                "Phone": flip["ReservationInfo"]["GuestInfo"]["Phone"],
                "Name": flip["ReservationInfo"]["GuestInfo"]["LastName"]+' '+flip["ReservationInfo"]["GuestInfo"]["FirstName"],
                "Address": flip["ReservationInfo"]["GuestInfo"]["Address"]
                },
            "HotelCode": flip["HotelInfo"]["HotelCode"],
            "HotelName": flip["HotelInfo"]["HotelName"],
            "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
            "FolioNo": flip["FolioNo"],
            "FolioCreatedDate": flip["BusinessDate"],
            "FolioCreatedDateTime": flip["BusinessDateTime"],
            "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
            "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
            "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["Name2"]+' '+flip["FolioInfo"]["PayeeInfo"]["Name3"],
            "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
            "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
            "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
            "NetAmount": flip["NetAmount"],
            "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
            "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
            "Postings": flip["FolioInfo"]["Postings"],
            "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }

    else:
        flip_info = {
            "id": pk,
            "EinvoiceInfo": {
                "EinvoiceNumber": flip["EinvoiceNumber"],
                "EinvoiceType": flip["EinvoiceType"],
                "EinvoiceStatus": flip["EinvoiceStatus"],
                "AuthorizedTaxCode": flip["AuthorizedTaxCode"],
                "EinvoiceFKey": flip["EinvoiceFKey"],
                "EinvoicePattern": flip["EinvoicePattern"],
                "EinvoiceSerial": "C23MAB",
                "EinvoiceAdjustDateTime": flip["EinvoiceAdjustDateTime"],
                "EinvoiceIssueDateTime": flip["EinvoiceIssueDateTime"]
            },
            "ConfirmationNo": flip["ReservationInfo"]["ConfirmationNo"],
            "Arrival": flip["ReservationInfo"]["ArrivalDate"],
            "Departure": flip["ReservationInfo"]["DepartureDate"],
            "GuestNo": str(int(flip["ReservationInfo"]["NumAdults"]) + int(flip["ReservationInfo"]["NumChilds"])),
            "RoomNo": flip["ReservationInfo"].get("RoomNumber"," "),
            "GuestInfo": flip["ReservationInfo"]["GuestInfo"],
            "HotelCode": flip["HotelInfo"]["HotelCode"],
            "HotelName": flip["HotelInfo"]["HotelName"],
            "AppUser": flip["FiscalFolioUserInfo"]["AppUser"],
            "FolioNo": flip["FolioNo"],
            "FolioCreatedDate": flip["BusinessDate"],
            "FolioCreatedDateTime": flip["BusinessDateTime"],
            "Window": flip["FolioInfo"]["FolioHeaderInfo"]["Window"],
            "RoomNumber": flip["ReservationInfo"]["RoomNumber"],
            "PayeeInfo": flip["FolioInfo"]["PayeeInfo"]["LastName"],
            "VATNo": flip["FolioInfo"]["PayeeInfo"]["Tax1No"],
            "PayeeAddress": flip["FolioInfo"]["PayeeInfo"]["Address"],
            "PaymentMethod": flip["FolioInfo"]["RevenueBucketInfo"][0]["BucketValue"],
            "NetAmount": flip["NetAmount"],
            "GrossAmount": flip["FolioInfo"]["TotalInfo"]["GrossAmount"],
            "Taxes": flip["FolioInfo"]["RevenueBucketInfo"],
            "Postings": flip["FolioInfo"]["Postings"],
            "TrxInfo": flip["FolioInfo"]["TrxInfo"]
        }

    return JsonResponse(flip_info, safe=False)


@api_view(['PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def folioupdate(request, pk):
    try:
        docobj = FlipInfo.objects.get(id=pk)
    except FlipInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        update_data = request.data
        docobj.EinvoiceNumber = update_data["EinvoiceNumber"]
        docobj.EinvoiceIssueDateTime = update_data["EinvoiceIssueDateTime"]
        docobj.EinvoiceType = update_data["EinvoiceType"]
        docobj.EinvoiceStatus = update_data["EinvoiceStatus"]
        docobj.AuthorizedTaxCode = update_data["AuthorizedTaxCode"]
        docobj.EinvoiceFKey = update_data["EinvoiceFKey"]
        docobj.EinvoicePattern = update_data["EinvoicePattern"]
        docobj.EinvoiceSerial = update_data["EinvoiceSerial"]
        
        docobj.save()

        message_status = {
            "The E-Invoice number has been updated:": {
                "EinvoiceNumber": update_data["EinvoiceNumber"],
                "EinvoiceIssueDateTime": update_data["EinvoiceIssueDateTime"],
                "EinvoiceType": update_data["EinvoiceType"],
                "EinvoiceStatus": update_data["EinvoiceStatus"],
                "AuthorizedTaxCode": update_data["AuthorizedTaxCode"],
                "EinvoiceFKey": update_data["EinvoiceFKey"],
                "EinvoicePattern": update_data["EinvoicePattern"],
                "EinvoiceSerial": update_data["EinvoiceSerial"]
            }
        }


        return Response(message_status, status=status.HTTP_200_OK)
    

@api_view(['PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def folioadjust(request, pk):
    try:
        docobj = FlipInfo.objects.get(id=pk)
    except FlipInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        update_data = request.data
        docobj.EinvoiceAdjustDateTime = update_data["EinvoiceAdjustDateTime"]
        docobj.save()

        message_status = {
            "The E-Invoice has been updated:": {
                "EinvoiceIssueDateTime": update_data["EinvoiceAdjustDateTime"]
            }
        }

        return Response(message_status, status=status.HTTP_200_OK, content_type='application/json')


class FlipViewSet(viewsets.ModelViewSet):
    queryset = FlipInfo.objects.all()
    serializer_class = FlipSerialize
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
