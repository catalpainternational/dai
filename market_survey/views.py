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
    c_grams_bought = {}
    c_grams_sold = {}
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
        veggies_weights = dict([((w.vegetable,w.survey),w.grams) for w in VegetableWeight.objects.all()])

        print "there are %d commodity to assess" % filter.qs.all().count()
        print "there are %d weights" % len(veggies_weights)

        n = 0
        grams_bought = 0.0
        grams_sold   = 0.0
        for c in filter.qs.all():
            k = (c.vegetable,c.vendor_survey.survey)

            if k in veggies_weights:
                c_grams_bought[c] = veggies_weights[k] * c.purchase_quantity
                c_grams_sold[c] = veggies_weights[k] * c.sale_quantity

                grams_bought += c_grams_bought[c]
                grams_sold   += c_grams_sold[c]
            else:
                n +=1 #print "no vegetable weight for ",k

        total_kg_bought = grams_bought * 0.001
        total_kg_sold = grams_sold * 0.001
        print "there are %d missing prices" % n
        print "time for total weight bought & sold method 1:",(datetime.now() - t0),'b:',total_kg_bought,'s:',total_kg_sold


        # t0 = datetime.now()
        # total_kg_bought = sum([c.total_kg_bought for c in filter.qs.all()])
        # total_kg_sold = sum([c.total_kg_sold for c in filter.qs.all()])
        # print "time for total weight bought & sold method 2:",(datetime.now() - t0),'b:',total_kg_bought,'s:',total_kg_sold

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
        response = export_as_csv(response, filter.qs, context)
        print "time for CSV export:",(datetime.now() - t0)
        return response

    print "Total time calculation:",(datetime.now() - t00)
    t0 = datetime.now()
    context['results_table_body']=get_results_tbody(request,c_grams_bought,c_grams_sold)
    print "Time for TBODY content rendering:",(datetime.now() - t0)

    t0 = datetime.now()
    response = render_to_response('market_survey/filter.html',
                              context,
                              context_instance=RequestContext(request))
    print "Time for HTML rendering:",(datetime.now() - t0)
    print "Total time:",(datetime.now() - t00)
    return response

def export_as_csv(response,queryset,context=None):

    writer = unicodecsv.writer(response)
    if context:
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

    for obj in queryset:
        writer.writerow([
            obj.vendor_survey,
            obj.vegetable ,
            obj.purchase_quantity ,
            "$ %2f" % obj.purchase_price,
            "$ %2f" %  obj.purchase_unit_price,
            obj.total_kg_bought,
            obj.sale_quantity,
            obj.sale_price,
            "$ %2f" % obj.total_dollars_sold,
            obj.total_kg_sold,
            obj.district ,
            "%2f %%" % obj.profit_margin])
    return response


def get_results_tbody(request,c_grams_bought,c_grams_sold):
    lines =[]
    for c in c_grams_sold.keys():

        vendor = c.vendor_survey
        if request.user.is_authenticated == True:
            vendor = "<a href='/market_survey/vendorsurvey/%d'> %s </a>" % (c.vendor_survey.id,c.vendor_survey)

        line = [
            "%s" % vendor,
            "%s" % c.vegetable.name,
            "%.2f kg" % (c_grams_bought[c] * 0.001),
            "%.2f kg" % (c_grams_sold[c] * 0.001),
            "$ %.2f" % c.purchase_price,
            "$ %.2f" % c.purchase_unit_price,
            "$ %.2f" % c.sale_price,
            "$ %.2f" % c.total_dollars_sold,
            "%s" % c.district,
            "%d %%" % c.profit_margin]
        # add missing vendor survey link

        line = "</td>\n\t\t\t<td>".join(line)
        lines.append(line)
    s = "<tr><td>" + "</td></tr>\n\t\t<tr>\n\t\t\t<td>".join(lines)
    return s
