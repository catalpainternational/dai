import django_filters
from django.utils.translation import ugettext_lazy as _

from models import Commodity


class CommodityFilter(django_filters.FilterSet):
    #purchase_price = django_filters.NumberFilter(lookup_type=['lte', 'gte', 'exact'])

    class Meta:
        model = Commodity
        fields = ['vegetable', 'district', 'vendor_survey__marketplace', 'vendor_survey__season']

    def __init__(self, *args, **kwargs):
        super(CommodityFilter, self).__init__(*args, **kwargs)
        self.filters['vegetable'].extra.update(
            {'empty_label': _(u'All Vegetables')})
        self.filters['vendor_survey__marketplace'].extra.update(
            {'empty_label': _(u'All Marketplaces')})
        self.filters['vendor_survey__season'].extra.update(
            {'empty_label': _(u'All Seasons')})
