from django.db import models


class FlipInfo(models.Model):
    DocumentInfo = models.JSONField()
    FiscalTerminalInfo = models.JSONField()
    FolioInfo = models.JSONField()
    HotelInfo = models.JSONField()
    ReservationInfo = models.JSONField()
    FiscalFolioUserInfo = models.JSONField()
    BusinessDate = models.DateField(blank=True, null=True)
    BusinessDateTime = models.DateTimeField(blank=True, null=True)
    FolioNo = models.CharField(max_length=500 ,default=0, null=True, blank=True)
    NetAmount = models.FloatField(default=0)
    EinvoiceNumber = models.CharField(max_length=500, null=True, blank=True, default=" ")
    EinvoiceType = models.CharField(max_length=200, null=True, blank=True, default="9: Not Upload")
    EinvoiceStatus = models.CharField(max_length=200, null=True, blank=True, default="9: Not Upload")
    EinvoiceFKey = models.CharField(max_length=200, default=" ")
    EinvoicePattern = models.CharField(max_length=200, default=" ")
    EinvoiceSerial = models.CharField(max_length=200, default=" ")
    AuthorizedTaxCode = models.CharField(max_length=500, null=True, blank=True, default=" ")
    EinvoiceAdjustDateTime = models.DateTimeField(blank=True, null=True)
    EinvoiceIssueDateTime = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return (self.EinvoiceStatus)

#EinvoiceStatus and EinvoiceType:
# 0: NewInv
# 1: Regular
# 2: Declare
# 3: Replaced
# 4: Adjusted
# 5: Cancelled
# 9: Not Upload