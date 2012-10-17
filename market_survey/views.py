import unicodecsv

from datetime import date
from datetime import datetime

from django.shortcuts import render_to_response
from django.db.models import Avg, Sum
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.template.context import RequestContext

from models import Commodity,VegetableWeight
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

        # Calculates weights
        t0 = datetime.now()
        veggies_infos = dict([((c.vegetable,c.vendor_survey.survey),[c.purchase_quantity,c.sale_quantity]) for c in filter.qs.all()])

        #hopefully, only one weight per vegetable | survey pair
        # ha!. Nope.
        just_veggies = [k[0] for k in veggies_infos.keys()]
        veggies_weights = dict([((w.vegetable,w.survey),w.grams) for w in VegetableWeight.objects.filter(vegetable__in=just_veggies)])

        grams_bought = 0
        grams_sold   = 0
        for k in veggies_infos.keys():
            if k in veggies_weights:
                grams_bought += veggies_weights[k] * float(veggies_infos[k][0])
                grams_sold   += veggies_weights[k] * float(veggies_infos[k][1])
            else:
                print "no vegetable weight for ",k

        #grams_bought = sum([veggies[v][0] * veggies_weights[v] for v in veggies.keys() if veggies_weights[v] != None])
        #grams_sold   = sum([veggies[v][1] * veggies_weights[v] for v in veggies.keys() if veggies_weights[v] != None])
        print "time for total weight bought & sold:",(datetime.now() - t0)

        total_kg_bought = grams_bought / 1000.0
        total_kg_sold = grams_sold / 1000.0

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

        response = export_as_csv(response, filter.qs, context)
        return response

    print "Total time calculation:",(datetime.now() - t00)
    response = render_to_response('market_survey/filter.html',
                              context,
                              context_instance=RequestContext(request))
    print "Total time:",(datetime.now() - t00)
    return response

def export_as_csv(response,queryset,context=None):

    writer = unicodecsv.writer(response)
    if context:
        header = [_('Filtered data summary'), date.today().strftime('%Y/%m/%d')]
        writer.writerow(header)
        columns =[
            _("Total Units bought"),
            _("Total $ bought"),
            _("Units $ bought"),
            _("Total Units sold"),
            _("Units $ sold"),
            _("Total $ sold"),
            _("Average Purchase"),
            _("Average Unit Sale"),
            _("Profit Margin")
        ]
        writer.writerow(columns)
        writer.writerow([
            context['total_units_bought'],
            "$ %2f" % context['total_dollars_bought'],
            "%2f" % context['unit_dollars_bought'],
            context['total_units_sold'],
            "%2f" % context['unit_dollars_sold'],
            "$ %2f" % context['total_dollars_sold'],
            "$ %2f" % context['avg_purchase'],
            "$ %2f" % context['avg_sale'],
            "%2f %%" % context['profit_margin']
        ])

    writer.writerow([_('Filtered data'), date.today().strftime('%Y/%m/%d')])
    writer.writerow([
        _('Vendor'),
        _('Vegetable'),
        _('Total Units bought'),
        _('Total $ bought'),
        _('Units $ bought'),
        _('Total Units sold'),
        _('Units $ sold'),
        _('Total $ sold'),
        _('District Origin'),
        _('Profit Margin')
    ])

    for obj in queryset:
        writer.writerow([
            obj.vendor_survey,
            obj.vegetable ,
            obj.purchase_quantity ,
            "$ %2f" % obj.purchase_price,
            "$ %2f" %  obj.purchase_unit_price,
            obj.sale_quantity,
            obj.sale_price,
            "$ %2f" % obj.total_dollars_sold,
            obj.district ,
            "%2f %%" % obj.profit_margin])
    return response
