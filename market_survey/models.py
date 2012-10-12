from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields import UUIDField


## Globals ##

# Distritu
DISTRICTS = (
             ('Aileu', 'Aileu'),
             ('Ainaro', 'Ainaro'),
             ('Baucau', 'Baucau'),
             ('Covalima', 'Covalima'),
             ('Dili', 'Dili'),
             ('Ermera', 'Ermera'),
             ('Lautem', 'Lautem'),
             ('Liquica', 'Liquica'),
             ('Manatutu', 'Manatutu'),
             ('Manufahi', 'Manufahi'),
             ('Oe-cussi', 'Oe-cussi'),
             ('Viqueque', 'Viqueque'),
             ('International', 'International')
             )

## End of Globals ##


class Survey(models.Model):
    uuid = UUIDField()
    name = models.CharField(max_length=128)
    month = models.IntegerField(choices=((x, x) for x in range(1, 13)))
    year = models.IntegerField(choices=((x, x) for x in range(2010, 2015)))

    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')

    def __unicode__(self,):
        return "%s (%s/%s)" % (self.name, self.month, self.year)


class Marketplace(models.Model):
    uuid = UUIDField()
    name = models.CharField(max_length=128)
    district = models.CharField(max_length=128, choices=DISTRICTS)

    class Meta:
        verbose_name = _('Marketplace')
        verbose_name_plural = _('Marketplaces')

    def __unicode__(self,):
        return "%s (%s)" % (self.name, self.district)


class Vegetable(models.Model):
    uuid = UUIDField()
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=128)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = _('Vegetable')
        verbose_name_plural = _('Vegetables')

    def __unicode__(self,):
        return "%s (%s)" % (self.name, self.unit)


class VegetableWeight(models.Model):
    uuid = UUIDField()
    survey = models.ForeignKey(Survey)
    vegetable = models.ForeignKey(Vegetable)
    grams = models.IntegerField()

    class Meta:
        verbose_name = _('Average Vegetable Weight')
        verbose_name_plural = _('Average Vegetable Weights')
        unique_together = (("survey", "vegetable"),)

    def __unicode__(self,):
        return u"%s (%s)" % (self.vegetable, self.survey)


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
    seasonal_shortage = models.BooleanField(_('Seasonal Shorage'))

    # Oin sa ita hetan modo hirak ne'e
    purchase_arrangement = models.CharField(_("Puchase Arrangement"), max_length=128, choices=SOURCES)

    # Ita sosa ho folin hira?
    purchase_quantity = models.IntegerField(_('quantity (bought)'))
    purchase_price = models.FloatField(_('price (bought)'))

    # Kuantiade nebe ita atou fa'an ohin
    sale_quantity = models.IntegerField(_('quantity (sold)'))
    sale_price = models.FloatField(_('Unit Price (sold)'))  # sale price per unit

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
    def total_dollars_sold(self,):
        total_dollars_sold = self.sale_price * self.sale_quantity
        return total_dollars_sold

    @property
    def profit_margin(self,):
        return int((self.sale_price - self.purchase_unit_price) / self.purchase_unit_price * 100)


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

    # Survey
    survey = models.ForeignKey(Survey)

    # Wainhira ita sosa modo, ita tenki selu keda ka fa'an tiha maka selu
    payment_timing = models.CharField(_('Payment timing'), max_length=128, choices=PAYMENT_TIMING_CHOICES)

    # Iha semana ida nia laran osan hira maka ita gasta hodi sosa modo (mais ou menus)
    payment_amount = models.CharField(_('Payment amount'), max_length=128, choices=PAYMENT_AMOUNT_CHOICES)

    # Ita fa'an mos ba vendedores seluk (fa'an ho gerobak ka vendedores seluk nebe fa'an haknaok)?
    on_sell_to_others = models.NullBooleanField(_('On sell to other vendors'))

    # Idade
    age_range = models.CharField(_('Age range'), max_length=128, choices=AGE_RANGE_CHOICES)

    # Sexu
    sex = models.CharField(_('Sex'), max_length=128, choices=GENDER)

    # market place
    marketplace = models.ForeignKey(Marketplace)

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')
        unique_together = (("vendor", "marketplace"),)


    def __unicode__(self):
        return "%s %s %s" % (self.vendor, self.marketplace, self.survey)
