import django_filters
from django.utils.translation import ugettext_lazy as _

from models import Commodity, Vegetable, Marketplace, DISTRICTS


class CommodityFilter(django_filters.FilterSet):
    #purchase_price = django_filters.NumberFilter(lookup_type=['lte', 'gte', 'exact'])
    vegetable = django_filters.ModelMultipleChoiceFilter(queryset=Vegetable.objects.all())
    vendor_survey__marketplace = django_filters.ModelMultipleChoiceFilter(queryset=Marketplace.objects.all())
    district = django_filters.MultipleChoiceFilter(choices=DISTRICTS)
    # Anders' code
    #vegetable = django_filters.MultipleChoiceFilter(choices=Vegetable.objects.all().values_list('pk', 'name'))
    # vendor_survey__marketplace = django_filters.MultipleChoiceFilter(choices=Marketplace.objects.all().values_list('pk','name'))


    class Meta:
        model = Commodity
        fields = ['vendor_survey__survey', 'vegetable', 'vendor_survey__marketplace', 'district',]

    def __init__(self, *args, **kwargs):
        super(CommodityFilter, self).__init__(*args, **kwargs)
        # self.filters['vegetable'].extra.update(
        #     {'empty_label': _(u'All Vegetables')})
        # self.filters['vendor_survey__marketplace'].extra.update(
        #     {'empty_label': _(u'All Marketplaces')})
        self.filters['vendor_survey__survey'].extra.update(
            {'empty_label': _(u'All Surveys')})