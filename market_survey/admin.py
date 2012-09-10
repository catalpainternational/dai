from django.contrib import admin
from django.db.models import IntegerField, FloatField
from django.forms import TextInput

from market_survey import models


class CommodityInline(admin.TabularInline):
    model = models.Commodity

    list_display = ['vegetable', 'district', 'vendor_survey__season']
    list_filter = ['vegetable', 'district', 'vendor_survey__season']

    formfield_overrides = {
        IntegerField: {'widget': TextInput(attrs={'style': 'width: 50px'})},
        FloatField: {'widget': TextInput(attrs={'style': 'width: 50px'})},
    }


class VendorSurveyAdmin(admin.ModelAdmin):
    model = models.VendorSurvey

    inlines = [
        CommodityInline,
    ]

    list_display = ['vendor', 'sex', 'age_range', 'marketplace', 'season', 'payment_amount']
    list_filter = ['sex', 'marketplace', 'season', 'payment_amount', 'age_range']
    search_fields = ['vendor', 'marketplace', 'marketplace__district', 'season']


class MarketplaceAdmin(admin.ModelAdmin):
    model = models.Marketplace

    list_display = ['name', 'district']
    list_filter = ['district']


class VegetableWeightAdmin(admin.ModelAdmin):
    model = models.VegetableWeight

    list_display = ['vegetable', 'season', 'grams']
    list_filter = ['vegetable', 'season']


class VegetableAdmin(admin.ModelAdmin):
    model = models.Vegetable

    list_display = ['name', 'unit', 'description']
    list_filter = ['name', 'unit']
    actions = []


admin.site.register(models.VendorSurvey, VendorSurveyAdmin)
admin.site.register(models.Marketplace, MarketplaceAdmin)
admin.site.register(models.Vegetable, VegetableAdmin)
admin.site.register(models.VegetableWeight, VegetableWeightAdmin)
admin.site.register(models.Season)

