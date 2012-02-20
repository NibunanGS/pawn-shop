from django.db import models
import datetime

# Create your models here.
class Ornament(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.name

class PersonName(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.name
    
class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    pincode = models.PositiveIntegerField(null=True, blank=True)
    #post = models.ForeignKey(City)
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(City, self).save(* args, **kwargs)
    
class Pledge(models.Model):
    STATUS_CHOICES = (
                      ('Open', 'Open'),
                      ('Closed', 'Closed'),
                      )
    
    pledge_no = models.CharField(max_length=10, unique=True)
    loan_date = models.DateField(default=datetime.datetime.now())
    principle = models.IntegerField()
    name = models.ForeignKey(PersonName, related_name='+')
    father_or_husband_name = models.ForeignKey(PersonName, related_name='+')
    address = models.TextField(null=True, blank=True)
    town = models.ForeignKey(City)
    net_weight = models.DecimalField(decimal_places=2, max_digits=5)
    advance_interest = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    document = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open', editable=False)
    
    def save(self, *args, **kwargs):
        self.advance_interest = (self.principle * 2) / 100
        if self.principle >= 2500:
            self.document = (self.principle * 0.5) / 100
        else:
            self.document = (self.principle * 1) / 100
        
        super(Pledge, self).save(* args, **kwargs) 

    def __unicode__(self):
        return "Ticket No:" + str(self.pledge_no) + ", Name:" + str(self.name) + ", Principle: " + str(self.principle)
    
class PledgedItem(models.Model):
    pledge = models.ForeignKey(Pledge)
    particulars = models.ForeignKey(Ornament)
    count = models.PositiveIntegerField()
    remarks = models.CharField(max_length=300, null=True, blank=True)
    
    def __unicode__(self):
        return "Pledge: [" + str(self.pledge) + "], Particulars:" + str(self.particulars) + ", Count:" + str(self.count)

class Redemption(models.Model):
    pledge = models.ForeignKey(Pledge, unique=True)
    date = models.DateField(default=datetime.datetime.now())
    interest = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    misc = models.IntegerField(null=True, blank=True)
    total = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    created = models.DateTimeField(editable=False, auto_now_add = True)
    updated = models.DateTimeField(editable=False, auto_now = True)
    
    def save(self, *args, **kwargs):
        start_date = self.pledge.loan_date
        end_date = self.date
        no_of_months = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month)
        if(end_date.day - start_date.day > 0):
            no_of_months = no_of_months + 1
        self.interest = ((self.pledge.principle * 2) / 100) * (no_of_months - 1)
        self.total = self.pledge.principle + self.interest
        
        self.pledge.status = "Closed"
        Pledge.save(self.pledge)
        super(Redemption, self).save(* args, **kwargs)
    
    def __unicode__(self):
        return "Pledge: [" + str(self.pledge) + "], Redemption Date:" + str(self.date) + ", Total:" + str(self.total)

class DailyRedemptionList(models.Model):
    date = models.DateField(default=datetime.datetime.now(), unique=True)
    principle = models.IntegerField()
    interest = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    misc = models.IntegerField(null=True, blank=True)
    total = models.DecimalField(decimal_places=2, max_digits=15, blank=True)
    created = models.DateTimeField(editable=False, auto_now_add = True)
    updated = models.DateTimeField(editable=False, auto_now = True)
    
    class Meta:
        ordering = ['-date']
    
    def __unicode__(self):
        return str(self.date) + "-> Principle" + str(self.principle) + ", Interest" + str(self.interest) + ", Misc" + str(self.misc) + ", Total:" + str(self.total)

