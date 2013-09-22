from django.db import models
import datetime
from django.core.exceptions import ValidationError

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
        
class Customer(models.Model):
    name_father_town = models.CharField(max_length=100, unique=True)
    name = models.ForeignKey(PersonName, related_name='+')
    father_or_husband_name = models.ForeignKey(PersonName, related_name='+')
    address = models.TextField(null=True, blank=True)
    town = models.ForeignKey(City)
    
    def clean(self):
        if self.id:
            previous_customer = Customer.objects.get(pk = self.id)
            if previous_customer.name != self.name or previous_customer.father_or_husband_name != self.father_or_husband_name or previous_customer.town != self.town:
                raise ValidationError("Please update the details in the Pledges, currently we won't be able to edit anything else then address here")
             
    
    def save(self, *args, **kwargs):
        self.name_father_town = str(self.name.id)+"-"+str(self.father_or_husband_name.id)+"-"+str(self.town.id) 
        super(Customer, self).save(* args, **kwargs) 

    def __unicode__(self):
        return "Name:" + str(self.name) + ", F/H Name: " + str(self.father_or_husband_name) + ", Town: " + str(self.town)
    
class DailyBalanceSheet(models.Model):
    date = models.DateField(default=datetime.datetime.now(), unique=True)
    previous_balance = models.IntegerField(default=0)
    credit = models.IntegerField(default=0)
    pledged_principle = models.IntegerField(default=0)
    redempted_advance_interest = models.IntegerField(default=0)
    document_charges = models.IntegerField(default=0)
    total_pledged_amount = models.IntegerField(default=0)
    redempted_principle = models.IntegerField(default=0)
    redempted_interest = models.IntegerField(default=0)
    redempted_misc_charges = models.IntegerField(default=0)
    total_redempted_amount = models.IntegerField(default=0)
    misc_debit = models.IntegerField(default=0)
    remarks = models.TextField(null=True, blank = True)
    amount_in_hand = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        self.total_pledged_amount = self.pledged_principle - self.redempted_advance_interest - self.document_charges
        self.total_redempted_amount = self.redempted_principle + self.redempted_interest + self.redempted_misc_charges
        self.amount_in_hand = self.previous_balance  + self.credit + self.total_redempted_amount - self.total_pledged_amount - self.misc_debit
        
        super(DailyBalanceSheet, self).save(* args, **kwargs)
    
    
    class Meta:
        ordering = ['-date']
        
    def __unicode__(self):
        return str(self.date) + "-> Total_Pledged_Amount:" + str(self.total_pledged_amount) + ", Total_Redempted_Amount:" + str(self.total_redempted_amount) + ", Amount_In_Hand:" + str(self.amount_in_hand)
    

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
    town = models.ForeignKey(City, related_name='+')
    customer = models.ForeignKey(Customer, editable=False)
    net_weight = models.DecimalField(decimal_places=2, max_digits=5)
    advance_interest = models.DecimalField(decimal_places=2, max_digits=10)
    document = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open', editable=False)
    daily_balance_sheet = models.ForeignKey(DailyBalanceSheet, editable=False, null = True)
    created = models.DateTimeField(editable=False, auto_now_add = True)
    updated = models.DateTimeField(editable=False, auto_now = True)
    
    def __set_the_customer(self):
            self.customer = Customer.objects.get_or_create(name = self.name, father_or_husband_name = self.father_or_husband_name, town = self.town)[0]
            
    def __add_to_balancesheet(self, balancesheet):
        balancesheet.pledged_principle = balancesheet.pledged_principle + self.principle
        balancesheet.redempted_advance_interest = balancesheet.redempted_advance_interest + self.advance_interest
        balancesheet.document_charges = balancesheet.document_charges + self.document
        
    def __detect_from_balancesheet(self, balancesheet, principle, interest, document):
        balancesheet.pledged_principle = balancesheet.pledged_principle - principle
        balancesheet.redempted_advance_interest = balancesheet.redempted_advance_interest - interest
        balancesheet.document_charges = balancesheet.document_charges - document
    
    def __updateDailyBalaceSheet(self):
        if not self.id: #New Pledge....
            balance_sheet = DailyBalanceSheet.objects.get_or_create(date = self.loan_date)[0]
            self.__add_to_balancesheet(balance_sheet)
            balance_sheet.save()
            self.daily_balance_sheet = balance_sheet
        else:
            previous_pledge = Pledge.objects.get(pk=self.id)
            if previous_pledge.loan_date == self.loan_date:
                # Only change in the principle amount
                if previous_pledge.principle != self.principle:
                    balance_sheet = DailyBalanceSheet.objects.get_or_create(date = self.loan_date)[0]
                    if previous_pledge.daily_balance_sheet:
                        self.__detect_from_balancesheet(balance_sheet, previous_pledge.principle, previous_pledge.advance_interest, previous_pledge.document) 
                    self.__add_to_balancesheet(balance_sheet);
                    balance_sheet.save()
                    self.daily_balance_sheet = balance_sheet
            else:
                balance_sheet = DailyBalanceSheet.objects.get_or_create(date = self.loan_date)[0]
                self.__add_to_balancesheet(balance_sheet)
                balance_sheet.save()
                self.daily_balance_sheet = balance_sheet
                
                previous_balance_sheet = previous_pledge.daily_balance_sheet
                if previous_balance_sheet:
                    self.__detect_from_balancesheet(previous_balance_sheet, previous_pledge.principle, previous_pledge.advance_interest, previous_pledge.document)
                    previous_balance_sheet.save()
                        
    
    def save(self, *args, **kwargs):
        self.pledge_no = self.pledge_no.upper()
        self.__set_the_customer()
        
        self.advance_interest = (self.principle * 2) / 100
        if self.principle > 5000 and self.principle < 6000:
            self.document = 150 - self.advance_interest
        elif self.principle >= 6000:
            self.document = (self.principle * 0.5) / 100
        else:
            self.document = (self.principle * 1) / 100
        
        self.__updateDailyBalaceSheet()
        super(Pledge, self).save(* args, **kwargs) 
        
    
    def delete(self):
        balanceSheet = self.daily_balance_sheet
        if balanceSheet:
            self.__detect_from_balancesheet(balanceSheet, self.principle, self.advance_interest, self.document)
            balanceSheet.save()
        super(Pledge, self).delete()

            
    def __unicode__(self):
        return "Ticket No:" + str(self.pledge_no) + ", Name:" + str(self.name) + ", Principle: " + str(self.principle)
    
class PledgedItem(models.Model):
    pledge_particulars = models.CharField(max_length=100, unique=True)
    pledge = models.ForeignKey(Pledge)
    particulars = models.ForeignKey(Ornament)
    count = models.PositiveIntegerField()
    remarks = models.CharField(max_length=300, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.pledge_particulars = str(self.pledge.id) +"-"+str(self.particulars.id)
        super(PledgedItem, self).save(* args, **kwargs)
    
    def __unicode__(self):
        return str(self.particulars) + ", Count:" + str(self.count)
    
class Redemption(models.Model):
    pledge = models.ForeignKey(Pledge, unique=True)
    date = models.DateField(default=datetime.datetime.now(), verbose_name = "Redemption Date")
    interest = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    misc = models.IntegerField(null=True, default=0)
    total = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    daily_balance_sheet = models.ForeignKey(DailyBalanceSheet, editable=False, null = True)
    created = models.DateTimeField(editable=False, auto_now_add = True)
    updated = models.DateTimeField(editable=False, auto_now = True)
    
    def pledge_no(self):
        return self.pledge.pledge_no
    pledge_no.short_description = 'Pledge No'
    
    def pledge_loan_date(self):
        return self.pledge.loan_date
    pledge_loan_date.short_description = 'Loan date'
    
    def pledge_principle(self):
        return self.pledge.principle
    pledge_principle.short_description = 'Principle'
    
    def pledge_customer_name(self):
        return self.pledge.name.name
    pledge_customer_name.short_description = 'Name'
    
    def __add_to_balancesheet(self, balancesheet):
        balancesheet.redempted_principle = balancesheet.redempted_principle + self.pledge.principle
        balancesheet.redempted_interest = balancesheet.redempted_interest + self.interest
        balancesheet.redempted_misc_charges = balancesheet.redempted_misc_charges + self.misc
        
    def __detect_from_balancesheet(self, balancesheet, principle, interest, misc):
        balancesheet.redempted_principle = balancesheet.redempted_principle - principle
        balancesheet.redempted_interest = balancesheet.redempted_interest - interest
        balancesheet.redempted_misc_charges = balancesheet.redempted_misc_charges - misc
        
    def __update_pledges_if_neccessary(self, previous_redemption):
        if previous_redemption.pledge.id != self.pledge.id:
            previous_redemption.pledge.status = "Open"
            Pledge.save(previous_redemption.pledge)
            self.pledge.status = "Closed"
            Pledge.save(self.pledge)
    
    def __update_dailybalacesheet_and_pledge(self):
        if not self.id: #New Redemption....
            self.pledge.status = "Closed"
            Pledge.save(self.pledge)

            balance_sheet = DailyBalanceSheet.objects.get_or_create(date = self.date)[0]
            self.__add_to_balancesheet(balance_sheet)
            balance_sheet.save()
            self.daily_balance_sheet = balance_sheet
        else:
            previous_redemption = Redemption.objects.get(pk=self.id)
            #Pledge change...
            self.__update_pledges_if_neccessary(previous_redemption)
            
            if previous_redemption.date == self.date:
                # Only change in the principle, interest & misc
                balance_sheet = DailyBalanceSheet.objects.get_or_create(date = self.date)[0]
                if previous_redemption.daily_balance_sheet:
                    self.__detect_from_balancesheet(balance_sheet, previous_redemption.pledge.principle, previous_redemption.interest, previous_redemption.misc) 
                self.__add_to_balancesheet(balance_sheet);
                balance_sheet.save()
                self.daily_balance_sheet = balance_sheet
            else:
                new_balance_sheet = DailyBalanceSheet.objects.get_or_create(date = self.date)[0]
                self.__add_to_balancesheet(new_balance_sheet)
                new_balance_sheet.save()
                self.daily_balance_sheet = new_balance_sheet
                
                previous_balance_sheet = previous_redemption.daily_balance_sheet
                if previous_balance_sheet:
                    self.__detect_from_balancesheet(previous_balance_sheet, previous_redemption.pledge.principle, previous_redemption.interest, previous_redemption.misc)
                    previous_balance_sheet.save()
                    
    def clean(self):
        if not self.date >= self.pledge.loan_date:
            raise ValidationError("Redemption date should be greater than or equal to loan date")
    
    def save(self, *args, **kwargs):
        start_date = self.pledge.loan_date
        end_date = self.date
        no_of_months = ((end_date.year - start_date.year) * 12) + (end_date.month - start_date.month)
        if(end_date.day - start_date.day > 0):
            no_of_months = no_of_months + 1
        
        if(no_of_months > 0):
            no_of_months = no_of_months - 1
        self.interest = ((self.pledge.principle * 2) / 100) * no_of_months
        self.total = self.pledge.principle + self.interest
        
        self.__update_dailybalacesheet_and_pledge()
        super(Redemption, self).save(* args, **kwargs)
        
    def delete(self):
        balanceSheet = self.daily_balance_sheet
        if balanceSheet:
            self.__detect_from_balancesheet(balanceSheet, self.pledge.principle, self.interest, self.misc)
            balanceSheet.save()
            
        self.pledge.status = "Open"
        Pledge.save(self.pledge)
        super(Redemption, self).delete()
    
    def __unicode__(self):
        return "Pledge: [" + str(self.pledge) + "], Redemption Date:" + str(self.date) + ", Total:" + str(self.total)
    
