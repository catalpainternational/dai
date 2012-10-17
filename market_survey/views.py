import unicodecsv

from datetime import date
from datetime import datetime

from django.shortcuts import render_to_response
from django.db.models import Avg, Sum
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.template.context import RequestContext

from models import Commodity,VegetableWeight,VendorSurvey
from filters import CommodityFilter



def index(request):
    return render_to_response('market_survey/index.html', context_instance=RequestContext(request))


def avg_product_list(request):
    t00 = datetime.now()
    filter = CommodityFilter(request.GET, queryset=Commodity.objects.all())
    context = {
        'filter': filter,
        'querystring': request.META['QUERY_STRING']
        }

    cache = {}
    if len(request.META['QUERY_STRING'])>0: # some filter
        total_units_bought = filter.qs.aggregate(Sum('purchase_quantity'))['purchase_quantity__sum']
        total_dollars_bought = filter.qs.aggregate(Sum('purchase_price'))['purchase_price__sum']

        unit_dollars_bought = None
        if total_dollars_bought > 0:
            unit_dollars_bought = total_dollars_bought / total_units_bought

        total_units_sold = filter.qs.aggregate(Sum('sale_quantity'))['sale_quantity__sum']
        unit_dollars_sold = filter.qs.aggregate(Sum('sale_price'))['sale_price__sum']
        total_dollars_sold = None

        if unit_dollars_sold != None and total_units_sold != None:
            t0 = datetime.now()
            total_dollars_sold = sum([ c.sale_price * c.sale_quantity for c in filter.qs.all()])
            print "time for unit total sold:",(datetime.now() - t0)


        t0 = datetime.now()
        # #hopefully, only one weight per vegetable | survey pair
        # # ha!. Nope.
        # get all the weights, independently of the survey
        veggies_weights = dict([((w['vegetable'],w['survey']),w['grams']) for w in VegetableWeight.objects.all().values('vegetable','grams','survey')])

        print "there are %d commodity to assess" % filter.qs.all().count()
        print "there are %d weights" % len(veggies_weights)
        grams_bought = 0
        grams_sold = 0
        weightless = 0
        fields = (
            'id',
            'vegetable',
            'vegetable__name',
            'vendor_survey',
            'vendor_survey__survey',
            'purchase_quantity',
            'purchase_price',
            'sale_quantity',
            'sale_price',
            'district')
        for c in filter.qs.all().values(*fields):
            buff = c

            buff['purchase_unit_price'] = 0 if c['purchase_price'] == 0 else  c['purchase_price'] / c['purchase_quantity']
            buff['total_dollars_sold'] = c['sale_price'] * c['sale_quantity']
            buff['profit_margin'] =  100 if buff['purchase_price']==0 else int((c['sale_price'] - buff['purchase_unit_price']) / buff['purchase_unit_price'] * 100)

            k = (c['vegetable'],c['vendor_survey__survey'])
            if k in veggies_weights:
                bought = veggies_weights[k] * int(c['purchase_quantity'])
                sold   = veggies_weights[k] * int(c['sale_quantity'])
                buff['grams_bought'] = bought
                buff['grams_sold']   = sold

                grams_bought += bought
                grams_sold   += sold
            else:
                buff['grams_bought'] = 0
                buff['grams_sold']   = 0
                weightless +=1
            cache[c['id']]=buff

        total_kg_bought = grams_bought * 0.001
        total_kg_sold = grams_sold * 0.001
        print "there are %d missing weights" % weightless
        print "time for total weight bought & sold method 1:",(datetime.now() - t0),'b:',total_kg_bought,'s:',total_kg_sold

        avg_sale = filter.qs.aggregate(Avg('sale_price'))['sale_price__avg']
        avg_purchase = filter.qs.aggregate(Avg('purchase_price'))['purchase_price__avg']

        profit_margin = None
        if unit_dollars_bought != None:
            profit_margin = int((avg_sale - unit_dollars_bought) / unit_dollars_bought * 100)

        context = {
            'filter': filter,
            'total_units_bought': total_units_bought,
            'total_dollars_bought': total_dollars_bought,
            'unit_dollars_bought': unit_dollars_bought,
            'total_kg_bought': total_kg_bought,
            'total_kg_sold': total_kg_sold,
            'total_units_sold': total_units_sold,
            'total_dollars_sold': total_dollars_sold,
            'unit_dollars_sold': unit_dollars_sold,
            'avg_sale': avg_sale,
            'avg_purchase': avg_purchase,
            'profit_margin': profit_margin,
            'querystring': request.META['QUERY_STRING']
        }

    if 'CSV' in request.GET:
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=market_survey_summarized_%s.csv' % date.today().strftime('%Y_%m_%d')
        t0 = datetime.now()
        response = export_as_csv(response, filter.qs, cache, context)
        print "time for CSV export:",(datetime.now() - t0)
        return response

    print "Total time calculation:",(datetime.now() - t00)
    t0 = datetime.now()
    context['results_table_body']=get_results_tbody(request,cache)
    print "Time for TBODY content rendering:",(datetime.now() - t0)

    t0 = datetime.now()
    response = render_to_response('market_survey/filter.html',
                              context,
                              context_instance=RequestContext(request))
    print "Time for HTML rendering:",(datetime.now() - t0)
    print "Total time:",(datetime.now() - t00)
    return response

def export_as_csv(response,queryset,cache,context):

    writer = unicodecsv.writer(response)
    header = [_('Filtered data summary'), date.today().strftime('%Y/%m/%d')]
    writer.writerow(header)
    columns =[
        _("Total Kg bought"),
        _("Total Kg sold"),
        _("Average Units $ bought"),
        _("Average Unit $ Sold"),
        _("Total $ sold"),
        _("Total $ sold"),
        _("Profit Margin"),
    ]
    writer.writerow(columns)
    writer.writerow([
        context['total_kg_bought'],
        context['total_kg_sold'],
        "$ %2f" % context['unit_dollars_bought'],
        "$ %2f" % context['avg_sale'],
        "$ %2f" % context['total_dollars_sold'],
        "%2f %%" % context['profit_margin']
    ])

    writer.writerow([_('Filtered data'), date.today().strftime('%Y/%m/%d')])
    writer.writerow([
        _('Vendor'),
        _('Vegetable'),
        _('Total Units bought'),
        _('Total $ bought'),
        _('Units $ bought'),
        _('Total Kg bought'),
        _('Total Units sold'),
        _('Units $ sold'),
        _('Total $ sold'),
        _('Total Kg sold'),
        _('District Origin'),
        _('Profit Margin')
    ])

    lines =[]
    vendors = dict([(v.id,v) for v in VendorSurvey.objects.all().select_related('marketplace')])
    for k in cache.keys():
        c = cache[k]
        survey_id = c['vendor_survey']
        vendor_survey = vendors[survey_id]
        line = [
            "%s" % vendor_survey,
            "%s" % c['vegetable__name'],
            "%d" % c['purchase_quantity'],
            "$ %.2f" % c['purchase_price'],
            "$ %.2f" % c['purchase_unit_price'],
            "%.2f kg" % (c['grams_bought'] * 0.001),
            "%d" % c['sale_quantity'],
            "$ %.2f" % c['sale_price'],
            "$ %.2f" % c['total_dollars_sold'],
            "%.2f kg" % (c['grams_sold'] * 0.001),
            "%s" % c['district'],
            "%d %%" % c['profit_margin']
        ]
        writer.writerow(line)

    return response


def get_results_tbody(request,cache):
    lines =[]
    vendors = dict([(v.id,v) for v in VendorSurvey.objects.all().select_related('marketplace')])
    for k in cache.keys():
        c = cache[k]
        survey_id = c['vendor_survey']
        vendor = vendors[survey_id]
        if request.user.is_authenticated == True:
            vendor = "<a href='/market_survey/vendorsurvey/%d'> %s </a>" % (c['vendor_survey'],vendor)

        line = [
            "%s" % vendor,
            "%s" % c['vegetable__name'],
            "%.2f kg" % (c['grams_bought'] * 0.001),
            "%.2f kg" % (c['grams_sold'] * 0.001),
            "$ %.2f" % c['purchase_price'],
            "$ %.2f" % c['purchase_unit_price'],
            "$ %.2f" % c['sale_price'],
            "$ %.2f" % c['total_dollars_sold'],
            "%s" % c['district'],
            "%d %%" % c['profit_margin']
        ]

        line = "</td>\n\t\t\t<td>".join(line)
        lines.append(line)
    s = "<tr><td>" + "</td></tr>\n\t\t<tr>\n\t\t\t<td>".join(lines)
    return s
