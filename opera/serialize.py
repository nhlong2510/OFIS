from rest_framework import serializers
from . models import Einvoice, OfisInfo


class EinvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Einvoice
        fields = (
            'EinvoiceNumber', 
            'EinvoiceType', 
            'EinvoiceStatus', 
            'EinvoiceFKey', 
            'EinvoicePattern', 
            'EinvoiceSerial', 
            'AuthorizedTaxCode', 
            'EinvoiceAdjustDateTime', 
            'EinvoiceIssueDateTime',
            )
        

class OfisInfoSerializer(serializers.ModelSerializer):
    EinvoiceInfo = EinvoiceSerializer(read_only=True)
    class Meta:
        model = OfisInfo
        fields = (
            'id',
            'EinvoiceInfo',
            'HotelCode',
            'HotelName',
            'AppUser',
            'ConfirmationNo',
            'Arrival',
            'Departure',
            'GuestNo',
            'GuestInfo',
            'FolioNo',
            'Window',
            'FolioType',
            'FolioCreatedDate',
            'FolioCreatedDateTime',
            'TerminalId',
            'Command',
            'RoomNumber',
            'PayeeInfo',
            'PayeeAddress',
            'VATNo',
            'PaymentMethod',
            'NetAmount',
            'GrossAmount',
            'Taxes',
            'Postings',
            'TrxInfo',
        )





