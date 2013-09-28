from PawnShop.pawnbrokerapp.models import Ornament, PersonName, City, Pledge, \
    Redemption, PledgedItem, Customer, DailyBalanceSheet
from django.contrib import admin
from django import forms
from django.contrib.admin.sites import site
from PawnShop.pawnbrokerapp.admin_utils import VerboseForeignKeyRawIdWidget

class PledgedItemInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        # get forms that actually have valid data
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise forms.ValidationError('We must have at least one pledged item')

class PledgedItemInline(admin.TabularInline):
    model = PledgedItem
    exclude = ['pledge_particulars']
    extra = 1
    formset = PledgedItemInlineFormset
    
class RedemptionInline(admin.TabularInline):
    model = Redemption
    extra = 0
    max_num = 1
    
class PledgeAdmin(admin.ModelAdmin):
    actions = None
    inlines = [PledgedItemInline, RedemptionInline]
    fields = ('loan_date','pledge_no', 'principle', 'name','father_or_husband_name','town','net_weight',('advance_interest','document'))
    readonly_fields = ('advance_interest','document')
    list_display = ( 'pledge_no','loan_date', 'name', 'father_or_husband_name','town', 'principle', 'net_weight')
    list_filter = ['loan_date', 'status']
    list_per_page = 25
    ordering = ['-loan_date', '-id']
    search_fields = ['pledge_no', 'name__name', 'father_or_husband_name__name', 'town__name', 'principle']
    date_hierarchy = 'loan_date'
    
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if isinstance(inline, RedemptionInline) and obj is None:
                continue
            yield inline.get_formset(request, obj), inline
            
admin.site.register(Pledge, PledgeAdmin)

class RedemptionAdmin(admin.ModelAdmin):
    actions_on_top = False
    actions_on_bottom = True
    list_display = ('pledge_no','pledge_customer_name','pledge_loan_date','pledge_principle','date', 'interest', 'total')
    list_filter = ['date']
    list_per_page = 25
    ordering = ['-date', '-id']
    search_fields = ['pledge__pledge_no', 'pledge__name__name', 'pledge__father_or_husband_name__name']
    date_hierarchy = 'date'
    raw_id_fields = ("pledge",)
    readonly_fields = ('interest', 'misc','total' )
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs.pop("request", None)
            type = db_field.rel.__class__.__name__
            if type == "ManyToOneRel":
                kwargs['widget'] = VerboseForeignKeyRawIdWidget(db_field.rel, site)
            return db_field.formfield(**kwargs)
        return super(RedemptionAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
admin.site.register(Redemption, RedemptionAdmin)

class CustomerAdmin(admin.ModelAdmin):
    actions = None
    fields = ('name','father_or_husband_name', 'address', 'town')
    list_display = ('name','father_or_husband_name','town')
    list_per_page = 25
    ordering = ['town__name', 'name__name', 'father_or_husband_name__name']
    search_fields = ['name__name', 'father_or_husband_name__name', 'town__name']
admin.site.register(Customer, CustomerAdmin)

class DailyBalanceSheetAdmin(admin.ModelAdmin):
    actions_on_top = False
    actions_on_bottom = True
    fields = ('date', ('previous_balance', 'credit'), ('pledged_principle', 'redempted_advance_interest', 'document_charges'), 'total_pledged_amount', ('redempted_principle', 'redempted_interest', 'redempted_misc_charges'), 'total_redempted_amount', 'misc_debit', 'amount_in_hand', 'remarks')
    readonly_fields = ('pledged_principle', 'redempted_advance_interest', 'document_charges', 'total_pledged_amount', 'redempted_principle', 'redempted_interest', 'total_redempted_amount')
    list_display = ('date', 'pledged_principle', 'total_pledged_amount', 'redempted_principle', 'total_redempted_amount', 'misc_debit','previous_balance', 'amount_in_hand')
    list_filter = ['date']
    list_per_page = 25
    ordering = ['-date']
    search_fields = ['date']
    date_hierarchy = 'date'
admin.site.register(DailyBalanceSheet, DailyBalanceSheetAdmin)

class OrnamentAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_per_page = 25
    ordering = ['name']
admin.site.register(Ornament, OrnamentAdmin)

class PersonNameAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_per_page = 25
    ordering = ['name']
admin.site.register(PersonName, PersonNameAdmin)

class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_per_page = 25
    ordering = ['name']
admin.site.register(City, CityAdmin)

