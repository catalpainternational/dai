from django.shortcuts import render_to_response

from models import Commodity
from filters import CommodityFilter

from django.db.models import Avg

def product_list(request):
    filter = CommodityFilter(request.GET, queryset=Commodity.objects.all())
    # This worked: filter.queryset.aggregate(Avg('sale_price'))
    return render_to_response('market_survey/filter.html', {'filter': filter})

def avg_product_list(request):
    filter = CommodityFilter(request.GET, queryset=Commodity.objects.all())
    # print filter.__dict__
    # print "---------"
    avg_sale = filter.qs.aggregate(Avg('sale_price'))
    avg_purchase = filter.qs.aggregate(Avg('purchase_price'))
    return render_to_response('market_survey/average.html', {'filter':filter,'avg_sale':avg_sale['sale_price__avg'],'avg_purchase':avg_purchase['purchase_price__avg']})
