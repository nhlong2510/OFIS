from django.db import models
from django.contrib.postgres.fields import ArrayField


class Einvoice(models.Model):
    EinvoiceNumber = models.CharField(max_length=500, null=True, blank=True, default=" ")
    EinvoiceType = models.CharField(max_length=200, null=True, blank=True, default="9: Not Upload")
    EinvoiceStatus = models.CharField(max_length=200, null=True, blank=True, default="9: Not Upload")
    EinvoiceFKey = models.CharField(max_length=200, default=" ")
    EinvoicePattern = models.CharField(max_length=200, default=" ")
    EinvoiceSerial = models.CharField(max_length=200, default=" ")
    AuthorizedTaxCode = models.CharField(max_length=500, null=True, blank=True, default=" ")
    EinvoiceAdjustDateTime = models.DateTimeField(blank=True, null=True)
    EinvoiceIssueDateTime = models.DateTimeField(blank=True, null=True)

#EinvoiceStatus and EinvoiceType:
# 0: NewInv
# 1: Regular
# 2: Declare
# 3: Replaced
# 4: Adjusted
# 5: Cancelled
# 9: Not Upload


class OfisInfo(models.Model):
    EinvoiceInfo = models.ForeignKey(Einvoice, related_name='invoice', on_delete=models.CASCADE)
    HotelCode = models.CharField(max_length=50)
    HotelName = models.CharField(max_length=200)
    AppUser = models.CharField(max_length=100)
    ConfirmationNo = models.CharField(max_length=100)
    Arrival = models.CharField(max_length=100)
    Departure = models.CharField(max_length=100)
    GuestNo = models.CharField(max_length=10)
    GuestInfo = models.JSONField()
    FolioNo = models.CharField(max_length=100, null=True, blank=True)
    Window = models.CharField(max_length=10)
    FolioType = models.CharField(max_length=100)
    FolioCreatedDate = models.CharField(max_length=100)
    FolioCreatedDateTime = models.CharField(max_length=100)
    TerminalId = models.CharField(max_length=200)
    Command = models.CharField(max_length=100)
    RoomNumber = models.CharField(max_length=50)
    PayeeInfo = models.CharField(max_length=500, null=True, blank=True)
    PayeeAddress = models.JSONField()
    VATNo = models.CharField(max_length=100, blank=True, null=True)
    PaymentMethod = models.CharField(max_length=50, default="TM/CK")
    # VAT8 = models.IntegerField(default=0)
    # VAT10 = models.IntegerField(default=0)
    # SVC = models.IntegerField(default=0)
    # SCT = models.IntegerField(default=0)
    NetAmount = models.BigIntegerField()
    GrossAmount = models.BigIntegerField()
    Taxes = ArrayField(models.JSONField())
    Postings = ArrayField(models.JSONField())
    TrxInfo = ArrayField(models.JSONField())
    
    def __str__(self):
        return f"Folio {self.FolioNo} created on {self.FolioCreatedDate} has the Einvoice Status {self.EinvoiceInfo.EinvoiceStatus}"
