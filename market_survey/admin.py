from django.contrib import admin
from django.db.models import IntegerField, FloatField
from django.forms import TextInput, RadioSelect

from market_survey import models


class CommodityInline(admin.TabularInline):
    model = models.Commodity

    list_display = ['vegetable', 'district', 'vendor_survey__survey']
    list_filter = ['vegetable', 'district', 'vendor_survey__survey']

    formfield_overrides = {
        IntegerField: {'widget': TextInput(attrs={'style': 'width: 50px'})},
        FloatField: {'widget': TextInput(attrs={'style': 'width: 50px'})},
    }


class VendorSurveyAdmin(admin.ModelAdmin):
    model = models.VendorSurvey

    inlines = [
        CommodityInline,
    ]

    list_display = ['vendor', 'sex', 'age_range', 'on_sell_to_others', 'marketplace', 'survey', 'payment_amount']
    list_filter = ['sex', 'marketplace', 'survey', 'payment_amount', 'on_sell_to_others', 'age_range']
    search_fields = ['marketplace__name', 'vendor', 'survey__name']

class MarketplaceAdmin(admin.ModelAdmin):
    model = models.Marketplace

    list_display = ['name', 'district']
    list_filter = ['district']


class VegetableWeightAdmin(admin.ModelAdmin):
    model = models.VegetableWeight

    list_display = ['vegetable', 'survey', 'grams']
    list_filter = ['vegetable', 'survey']


class VegetableAdmin(admin.ModelAdmin):
    model = models.Vegetable

    list_display = ['name', 'unit', 'description']
    list_filter = ['name', 'unit']
    actions = []


admin.site.register(models.VendorSurvey, VendorSurveyAdmin)
admin.site.register(models.Marketplace, MarketplaceAdmin)
admin.site.register(models.Vegetable, VegetableAdmin)
admin.site.register(models.VegetableWeight, VegetableWeightAdmin)
admin.site.register(models.Survey)

