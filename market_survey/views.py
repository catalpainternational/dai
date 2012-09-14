from django.shortcuts import render_to_response

from models import Commodity
from filters import CommodityFilter

from django.db.models import Avg, Sum


def index(request):
    return render_to_response('market_survey/index.html')


def product_list(request):
    filter = CommodityFilter(request.GET, queryset=Commodity.objects.all())
    # This worked: filter.queryset.aggregate(Avg('sale_price'))
    return render_to_response('market_survey/filter.html', {'filter': filter})


def avg_product_list(request):
    filter = CommodityFilter(request.GET, queryset=Commodity.objects.all())
    # print filter.__dict__
    # print "---------"

    total_units_bought = filter.qs.count()
    total_dollars_bought = filter.qs.aggregate(Sum('purchase_price'))['purchase_price__sum']

    unit_dollars_bought = None
    if total_dollars_bought > 0:
        unit_dollars_bought = total_units_bought / total_dollars_bought

    total_unit_grams_bought = None

    total_units_sold = filter.qs.count()
    total_dollars_sold = filter.qs.aggregate(Sum('sale_price'))['sale_price__sum']

    unit_dollars_sold = None
    if total_dollars_sold > 0:
        unit_dollars_sold = total_units_sold / total_dollars_sold

    avg_sale = filter.qs.aggregate(Avg('sale_price'))['sale_price__avg']
    avg_purchase = filter.qs.aggregate(Avg('purchase_price'))['purchase_price__avg']

    profit_margin = None
    if avg_purchase > 0:
        profit_margin = int((avg_sale - avg_purchase) / avg_purchase * 100)

    return render_to_response('market_survey/average.html', 
                              {'filter': filter,
                              'total_units_bought': total_units_bought,
                              'total_dollars_bought': total_dollars_bought,
                              'unit_dollars_bought': unit_dollars_bought,
                              'total_unit_grams_bought': total_unit_grams_bought,
                              'total_units_sold': total_units_sold,
                              'total_dollars_sold': total_dollars_sold,
                              'unit_dollars_sold': unit_dollars_sold,
                              'avg_sale': avg_sale,
                              'avg_purchase': avg_purchase,
                              'profit_margin': profit_margin,
                              })
