from PawnShop.pawnbrokerapp.models import Ornament, PersonName, City, Pledge, \
    Redemption, PledgedItem
from django.contrib import admin

class PledgedItemInline(admin.TabularInline):
    model = PledgedItem
    extra = 1
class PledgeAdmin(admin.ModelAdmin):
    inlines = [PledgedItemInline]
    list_display = ('loan_date', 'pledge_no', 'name', 'town', 'principle', 'net_weight')
    list_filter = ['loan_date', 'status', 'name']
    search_fields = ['pledge_no', 'name__name', 'father_or_husband_name__name', 'town__name', 'principle']
    date_hierarchy = 'loan_date'
admin.site.register(Pledge, PledgeAdmin)


class RedemptionAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    search_fields = ['pledge__pledge_no', 'pledge__name__name', 'pledge__father_or_husband_name__name']
admin.site.register(Redemption, RedemptionAdmin)



class OrnamentAdmin(admin.ModelAdmin):
    search_fields = ['name']
admin.site.register(Ornament, OrnamentAdmin)

class PersonNameAdmin(admin.ModelAdmin):
    search_fields = ['name']
admin.site.register(PersonName, PersonNameAdmin)

class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
admin.site.register(City, CityAdmin)

