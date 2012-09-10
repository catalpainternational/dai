from django.shortcuts import render_to_response

from models import Commodity
from filters import CommodityFilter


def product_list(request):
    filter = CommodityFilter(request.GET, queryset=Commodity.objects.all())

    return render_to_response('market_survey/filter.html', {'filter': filter})
