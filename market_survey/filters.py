from django.utils.translation import ugettext_lazy as _
from django import forms

import django_filters

from models import Survey, Commodity, Vegetable, Marketplace, DISTRICTS


class CommodityFilter(django_filters.FilterSet):
    vendor_survey__survey = django_filters.ModelMultipleChoiceFilter(label=_('Surveys'), widget=forms.CheckboxSelectMultiple, queryset=Survey.objects.all())
    vegetable = django_filters.ModelMultipleChoiceFilter(label=_('Vegetable'), widget=forms.CheckboxSelectMultiple, queryset=Vegetable.objects.all())
    vendor_survey__marketplace = django_filters.ModelMultipleChoiceFilter(label=_('Marketplace'), widget=forms.CheckboxSelectMultiple,  queryset=Marketplace.objects.all())
    district = django_filters.MultipleChoiceFilter(label=_('District'), widget=forms.CheckboxSelectMultiple, choices=DISTRICTS)


    class Meta:
        model = Commodity
        fields = ['vendor_survey__survey', 'vegetable', 'vendor_survey__marketplace', 'district',]

    def __init__(self, *args, **kwargs):
        super(CommodityFilter, self).__init__(*args, **kwargs)
        # self.filters['vegetable'].extra.update(
        #     {'empty_label': _(u'All Vegetables')})
        # self.filters['vendor_survey__marketplace'].extra.update(
        #     {'empty_label': _(u'All Marketplaces')})
        # self.filters['vendor_survey__survey'].extra.update(
        #     {'empty_label': _('All Surveys')})