from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields import UUIDField


## Globals ##

# Distritu
DISTRICTS = (
             ('Aileiu', 'Aileiu'),
             ('Ainaro', 'Ainaro'),
             ('Baucau', 'Baucau'),
             ('Covolima', 'Covolima'),
             ('Dili', 'Dili'),
             ('Ermera', 'Ermera'),
             ('Lautem', 'Lautem'),
             ('Liquica', 'Liquica'),
             ('Manatutu', 'Manatutu'),
             ('Manufahi', 'Manufahi'),
             ('Oe-cussi', 'Oe-cussi'),
             ('Viqueque', 'Viqueque'),
             )

## End of Globals ##


class Season(models.Model):
    uuid = UUIDField()
    name = models.CharField(max_length=128)
    month = models.IntegerField(choices=((x, x) for x in range(1, 13)))
    year = models.IntegerField(choices=((x, x) for x in range(2010, 2015)))

    def __unicode__(self,):
        return "%s (%s/%s)" % (self.name, self.month, self.year)


class Marketplace(models.Model):
    uuid = UUIDField()
    name = models.CharField(max_length=128)
    district = models.CharField(max_length=128, choices=DISTRICTS)

    def __unicode__(self,):
        return "%s (%s)" % (self.name, self.district)


class Vegetable(models.Model):
    uuid = UUIDField()
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=128)
    description = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self,):
        return "%s (%s)" % (self.name, self.unit)


class VegetableWeight(models.Model):
    uuid = UUIDField()
    season = models.ForeignKey(Season)
    vegetable = models.ForeignKey(Vegetable)
    grams = models.IntegerField()

    def __unicode__(self,):
        return u"%s (%s)" % (self.vegetable, self.season)


class Commodity(models.Model):

    ## Choices ##

    # Komersiantes lori ho truk ba merkadu
        # Langganan
        # Modo resin

    # Modo nebe sosa husi agrikultor ka truk nebe imi konhese hodi hameno uluk tiha
        # Komersiante Individual
        # Membru Grupu sosa hamutuk

    # Husi ne'ebe
        # Ba distritu ida idak hodi sosa rasik
        # Halo kontratu ho Agrikultor
        # Produs rasik

    SOURCES = (
               ('Langganan', _('Langganan')),
               ('Modo resin', _('Modo resin')),
               ('Komersiante Individual', _('Komersiante Individual')),
               ('Membru Grupu sosa hamutuk', _('Membru Grupu sosa hamutuk')),
               ('Ba distritu ida idak hodi sosa rasik', _('Ba distritu ida idak hodi sosa rasik')),
               ('Halo kontratu ho Agrikultor', _('Halo kontratu ho Agrikultor')),
               ('Produs rasik', _('Produs rasik')),
               )

    uuid = UUIDField()

    # Vendor
    vendor_survey = models.ForeignKey('VendorSurvey')

    # Unidade
    vegetable = models.ForeignKey(Vegetable)

    # Menus iha tempu balun
    seasonal = models.BooleanField()

    # Oin sa ita hetan modo hirak ne'e
    source_of_vegetable = models.CharField(max_length=128, choices=SOURCES)

    # Ita sosa ho folin hira?
    purchase_quantity = models.IntegerField(_('quantity (buy)'))
    purchase_price = models.FloatField(_('price (buy)'))

    # Kuantiade nebe ita atou fa'an ohin
    sale_quantity = models.IntegerField(_('quantity (sell)'))
    sale_price = models.FloatField(_('price (sell)'))

     # Distritu nebe mak kuda modo hirak ne'e
    district = models.CharField(_('District Origin'), max_length=128, choices=DISTRICTS)

    class Meta:
        verbose_name = _('Commodity')
        verbose_name_plural = _('Commodities')

    def __unicode__(self):
        return "%s (%s) - %s" % (self.vegetable, self.district, self.vendor_survey)


    @property
    def purchase_unit_price(self,):
        p_unit_price = self.purchase_price / self.purchase_quantity
        return p_unit_price


    @property
    def sale_unit_price(self,):
        s_unit_price = self.sale_price / self.sale_quantity
        return s_unit_price


    @property
    def profit_margin(self,):
        return int((self.sale_unit_price - self.purchase_unit_price) / self.purchase_unit_price * 100)



class VendorSurvey(models.Model):

    ## Choices ##
    PAYMENT_TIMING_CHOICES = (
               ('kedas', _('Selu kedas')),
               ('depois', _('Depois maka selu')),
              )

    PAYMENT_AMOUNT_CHOICES = (
                      ('$50', '$50'),
                      ('$51 - $200', '$51 - $200'),
                      ('$200 - $300', '$200 - $300'),
                      ('$300+', '$300+'),
                      )

    AGE_RANGE_CHOICES = (
                         ('Less than 20', _('Less than 20')),
                         ('20 - 50', _('20 - 50')),
                         ('50 years or more', _('50 years or more')),
                         )

    GENDER = (
           ('M', _('Male')),
           ('F', _('Female')),
           )

    # UUID
    uuid = UUIDField()

    # Vendor Number
    vendor = models.IntegerField(_('Vendor Number'))

    # Season
    season = models.ForeignKey(Season)

    # Wainhira ita sosa modo, ita tenki selu keda ka fa'an tiha maka selu
    payment_timing = models.CharField(max_length=128, choices=PAYMENT_TIMING_CHOICES)

    # Iha semana ida nia laran osan hira maka ita gasta hodi sosa modo (mais ou menus)
    payment_amount = models.CharField(max_length=128, choices=PAYMENT_AMOUNT_CHOICES)

    # Idade
    age_range = models.CharField(max_length=128, choices=AGE_RANGE_CHOICES)

    # Sexu
    sex = models.CharField(max_length=128, choices=GENDER)

    # market place
    marketplace = models.ForeignKey(Marketplace)

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')

    def __unicode__(self):
        return "%s %s %s" % (self.vendor, self.marketplace, self.season)
