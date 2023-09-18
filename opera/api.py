from datetime import date, datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from . models import OfisInfo, Einvoice
from . filters import OfisFilter
from . pagination import MyPagination
from . serializers import OfisInfoSerializer


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def foliocreate(request):
    new_einvoice = Einvoice.objects.create(
        EinvoiceType = "9: Not Upload",
        EinvoiceStatus = "9: Not Upload",
    )
    new_einvoice.save()

    post_data = request.data
    postings = post_data["FolioInfo"].get("Postings", [])
    trxinfo = post_data["FolioInfo"].get("TrxInfo", [])
    net_amount = post_data["FolioInfo"].get("TotalInfo", {}).get("NetAmount", 0)
    bucketinfo = post_data["FolioInfo"].get("RevenueBucketInfo", [])
    mop = "TM/CK"
    for bucket in bucketinfo:
        if bucket.get("BucketType") != "FLIP_PAY_TYPE":
            mop = bucket["Description"]
    
    # taxes = post_data["FolioInfo"].get("TotalInfo", {}).get("Taxes", {}).get("Tax", [])
    # if svc trx codes are set as non tax type and all trx codes are set as taxes exclusive:
    # for bucket in bucketinfo:
    #     if bucket.get("Description") == "SVC":
    #         net_amount -= bucket["BucketCodeTotalGross"]
    
    # if all trx codes are set as taxes inclusive and POS postings are taxes exclusive:
    # for tax in taxes:
    #     if tax.get("Percent") == "5.00":
    #         net_amount -= tax["Value"]
    
    for item_a in postings:
        for item_b in trxinfo:
            if item_a.get("TrxCode") == item_b.get("Code") and item_a.get("TrxType") == item_b.get("TrxType"):
                item_a["Group"] = item_b["Group"]
                item_a["SubGroup"] = item_b["SubGroup"]
    new_postings = [item for item in postings if "GuestAccountDebit" in item or "GuestAccountCredit" in item]

    for item in new_postings:
        if "NetAmount" not in item and "GuestAccountDebit" in item:
            item["NetAmount"] = item["UnitPrice"]
            item["GrossAmount"] = item["GuestAccountDebit"]
    payeeinfo = ""
    vatno = ""
    if post_data["FolioInfo"].get("PayeeInfo", {}).get("NameType", "INDIVIDUAL") == "INDIVIDUAL":
        payeeinfo = post_data["FolioInfo"]["PayeeInfo"]["Address"].get("Address1", post_data["ReservationInfo"].get("GuestInfo",{}).get("LastName", " ")+' '+post_data["ReservationInfo"].get("GuestInfo",{}).get("FirstName", " "))
        vatno = post_data["FolioInfo"]["PayeeInfo"]["Address"].get("Address4", "")
    else:
        payeeinfo = post_data["FolioInfo"]["PayeeInfo"].get("Name2",post_data["FolioInfo"]["PayeeInfo"].get("LastName"," "))
        vatno = post_data["FolioInfo"]["PayeeInfo"].get("Tax1No","")
    payeeaddress = {
            "Address1": post_data["FolioInfo"]["PayeeInfo"]["Address"].get("Address2", ""),
            "Address2": post_data["FolioInfo"]["PayeeInfo"]["Address"].get("Address3", ""),
            "City": post_data["FolioInfo"]["PayeeInfo"]["Address"].get("City", ""),
            "Country": post_data["FolioInfo"]["PayeeInfo"]["Address"].get("AddresseeCountryDesc", "Viet Nam"),
        }
    
    if post_data["ReservationInfo"].get("GuestInfo",{}).get("IdentificationInfos",{}).get("IdentificationInfo", []):
        id_type = post_data["ReservationInfo"]["GuestInfo"]["IdentificationInfos"]["IdentificationInfo"][0].get("IdType", "")
        id_number = post_data["ReservationInfo"]["GuestInfo"]["IdentificationInfos"]["IdentificationInfo"][0].get("IdNumber", "")
    
    if post_data.get("ReservationInfo",{}).get("RoomType") not in ["PF","PI"] and post_data.get("FolioInfo",{}).get("TotalInfo",{}).get("NetAmount",0) > 0:
        new_folio = OfisInfo.objects.create(
            EinvoiceInfo = new_einvoice,
            HotelCode = post_data["DocumentInfo"]["HotelCode"],
            HotelName = post_data["HotelInfo"]["HotelName"],
            AppUser = post_data["FiscalFolioUserInfo"]["AppUser"],
            ConfirmationNo = post_data["ReservationInfo"]["ConfirmationNo"],
            Arrival = post_data["ReservationInfo"]["ArrivalDate"],
            Departure = post_data["ReservationInfo"]["DepartureDate"],
            GuestNo = post_data["ReservationInfo"]["NumAdults"]+"/"+post_data["ReservationInfo"]["NumChilds"],
            GuestInfo = {
                "FirstName": post_data["ReservationInfo"].get("GuestInfo",{}).get("FirstName", " "),
                "LastName": post_data["ReservationInfo"].get("GuestInfo",{}).get("LastName", " "),
                "DateOfBirth": post_data["ReservationInfo"].get("GuestInfo",{}).get("DateOfBirth", " "),
                "IdType": id_type,
                "IdNumber": id_number,
                "Nationality": post_data["ReservationInfo"].get("GuestInfo",{}).get("Nationality", "VN"),
                "Address": post_data["ReservationInfo"].get("GuestInfo",{}).get("Address", {}),
                "Email": post_data["ReservationInfo"].get("GuestInfo",{}).get("Email", " "),
                "Phone": post_data["ReservationInfo"].get("GuestInfo",{}).get("Phone", {})
            },
            FolioNo = post_data["DocumentInfo"]["BillNo"],
            Window = post_data["FolioInfo"]["FolioHeaderInfo"]["Window"] if post_data["FolioInfo"].get("FolioHeaderInfo") is not None else "",
            FolioType = post_data["DocumentInfo"]["FolioType"],
            FolioCreatedDate = date.today().strftime("%Y-%m-%d'),
            FolioCreatedDateTime = datetime.today().strftime("&Y-%m-%dT%H:%M:%S"),
            TerminalId = post_data.get("FiscalTerminalInfo", {}).get("TerminalId", ""),
            Command = post_data["DocumentInfo"]["Command"],
            RoomNumber = post_data["ReservationInfo"]["RoomNumber"],
            PayeeInfo = payeeinfo,
            PayeeAddress = payeeaddress,
            VATNo = vatno,
            PaymentMethod = mop,
            NetAmount = net_amount,
            GrossAmount = post_data["FolioInfo"].get("TotalInfo", {}).get("GrossAmount", 0),
            Taxes = bucketinfo,
            Postings = new_postings,
            TrxInfo = trxinfo,
        )
        new_folio.save()

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

        return Response(message_status)
    else:
        message_status = {
            "FiscalFolioNo": '',
            "FiscalBillGenerationDateTime": '',
            "FiscalOutput": {
                "Name": "DATA_TO_EINVOICE",
                "Value": ""
            },
                "StatusMessage": {
                    "Message": {
                        "Description": "Folio is not posted because Net Amount is 0 or room type is PF/PI, successful response",
                        "Type": "COMPLETED"
                    }
                }
            }
        return Response(message_status)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def folioinfo(request):
    folio_info = OfisInfo.objects.all()
    folio_filterset = OfisFilter(request.GET, queryset=folio_info)
    if folio_filterset.is_valid:
        folio_info = folio_filterset.qs
    paginator = MyPagination()
    page = paginator.paginate_queryset(folio_info, request)
    serializer = OfisInfoSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def foliodetail(request, pk):
    folio_detail = OfisInfo.objects.get(pk=pk)
    serializer = OfisInfoSerializer(folio_detail)

    return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def folioupdate(request, pk):
    invoice_obj = OfisInfo.objects.get(pk=pk).EinvoiceInfo
    
    update_data = request.data
    invoice_obj.EinvoiceNumber = update_data["EinvoiceNumber"]
    invoice_obj.EinvoiceIssueDateTime = update_data["EinvoiceIssueDateTime"]
    invoice_obj.EinvoiceType = update_data["EinvoiceType"]
    invoice_obj.EinvoiceStatus = update_data["EinvoiceStatus"]
    invoice_obj.AuthorizedTaxCode = update_data["AuthorizedTaxCode"]
    invoice_obj.EinvoiceFKey = update_data["EinvoiceFKey"]
    invoice_obj.EinvoicePattern = update_data["EinvoicePattern"]
    invoice_obj.EinvoiceSerial = update_data["EinvoiceSerial"]
    
    invoice_obj.save()

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
