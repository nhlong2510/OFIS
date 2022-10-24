from rest_framework import serializers
from . models import FlipInfo


class FlipSerialize(serializers.ModelSerializer):
    class Meta:
        model = FlipInfo
        fields = [
            "id",
            "EinvoiceNumber",
            "EinvoiceType",
            "EinvoiceStatus",
            "AuthorizedTaxCode",
            "EinvoiceFKey",
            "EinvoicePattern",
            "EinvoiceSerial",
            "EinvoiceIssueDateTime",
            "EinvoiceAdjustDateTime",
            "BusinessDate",
            "BusinessDateTime",
            "FolioNo",
            "NetAmount",
            "DocumentInfo",
            "FolioInfo",
            "HotelInfo",
            "ReservationInfo",
            "FiscalTerminalInfo",
            "FiscalFolioUserInfo",
        ]
    

class OFISSerialize(serializers.ModelSerializer):
    class Meta:
        model = FlipInfo
        fields = '__all__'