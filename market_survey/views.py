import unicodecsv

from datetime import date
from django.shortcuts import render_to_response
from django.db.models import Avg, Sum
from django.utils.translation import ugettext as _
from django.http import HttpResponse

from models import Commodity
from filters import CommodityFilter



def index(request):
    return render_to_response('market_survey/index.html')


def product_list(request):
    filter = CommodityFilter(request.GET, queryset=Commodity.objects.all())
    # This worked: filter.queryset.aggregate(Avg('sale_price'))
    print "--",request.GET
    if 'CSV' in request.GET:
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=market_survey_filtered_%s.csv' % date.today().strftime('%Y_%m_%d')

        response = export_as_csv(response,filter.qs)
        return response
    else:
        return render_to_response('market_survey/filter.html', {'filter': filter, 'querystring':request.META['QUERY_STRING']})


def avg_product_list(request):
    filter = CommodityFilter(request.GET, queryset=Commodity.objects.all())

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



def export_as_csv(response,queryset):

    header = [_('Filtered data'), date.today().strftime('%Y/%m/%d')]
    writer = unicodecsv.writer(response)
    columns =[
        _('Vendor'),
        _('Vegetable'),
        _('Purchase Price'),
        _('Purchase Quantity'),
        _('Purchase Unit Price'),
        _('Sale Price'),
        _('Sale Quantity'),
        _('Sale Unit Price'),
        _('District Origin'),
        _('Profit Margin')
    ]

    writer.writerow(header)
    writer.writerow(columns)
    for obj in queryset:
        writer.writerow([
            obj.vendor_survey,
            obj.vegetable ,
            "$ %2f" % obj.purchase_price,
            obj.purchase_quantity ,
            "$ %2f" %  obj.purchase_unit_price,
            obj.sale_price,
            obj.sale_quantity ,
            "$ %2f" % obj.sale_unit_price,
            obj.district ,
            obj.profit_margin])
    return response