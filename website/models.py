from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone


# SOURCE_CHOICES
SOURCE_CHOICES = (
    ('1', 'DATABASE'),
    ('2', 'LINUX BOX')
)

# RESULTS_DATATYPE_CHOICES
RESULTS_DATATYPE_CHOICES = (
    ('1', 'INTEGER'),
    ('2', 'FLOAT'),
    ('3', 'STRING/TEXT'),
    ('4', 'PYTHON LIST OR DICTIONARY')
)

# COLOR_RANGE_CHOICES
COLOR_RANGE_CHOICES = (
    ('1', 'YELLOW'),
    ('2', 'RED'),
    ('3' ,'ORANGE'),
    ('4', 'BLUE'),
    ('5', 'PURPLE'),
    ('6', 'GREEN'),
    ('7', 'BROWN'),
    ('8', 'MAGENTA')   
)




# Configuration Rules Model Manager
class ConfigurationRulesManager(models.Manager):
    def get_queryset(self):
        return super(ConfigurationRulesManager,self).get_queryset().order_by('header')



# Negatice Number Validator
def NegativeNumebrValidator(value):
    if value < 0:
        raise ValidationError("Number should be greater than 0.")

class Fruit(models.Model):
    Name = models.CharField(
        max_length=30, 
        unique = False, 
        default = '', 
        blank=False,
        help_text="Name of the Fruit.",
        error_messages = {
            'blank' : "Name of the fruit should be provided."
        },
        verbose_name = "Fruit Name"
    )
    Price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        unique = False,
        default=0.0,
        blank = False,
        help_text = "Price of the Fruit.",
        error_messages = {
            'blank' : "Price of the fruit should be provided."
        },
        verbose_name = "Fruit Price",
        validators = [
            NegativeNumebrValidator
        ]
    )
    Color = models.CharField(
        max_length=30, 
        unique = False, 
        default = '', 
        blank=False,
        help_text="Color of the Fruit.",
        error_messages = {
            'blank' : "Color of the fruit should be provided."
        },
        verbose_name = "Fruit Color"
    )

    def __str__(self):
        return "{Name}-{Color}-{Price}".format(Name = self.Name, Color= self.Color, Price = self.Price)

    class Meta:
        verbose_name = "Fruit"
        verbose_name_plural  = "Fruits"
        ordering = [
            "-id"
        ]
        db_table = "fruit"

class QueryResult(models.Model):
    user = models.ForeignKey(
        get_user_model(), 
        on_delete = models.CASCADE
    )
    query = models.CharField(
        max_length = 300, 
        default="", 
        blank = False,
        verbose_name = "MySQL Query",
        help_text = "MySQL Query",
        error_messages = {
            'blank' : "Query should be provided."
        },
    )
    stamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name = "Query Created Date and Time"
    )

    def __str__(self):
        return "{User}-{Query}-{stamp}".format(User=self.user.username, Query = self.query, stamp = self.stamp)

    class Meta:
        verbose_name = "Query"
        verbose_name_plural  = "Queries"
        ordering = [
            "-stamp"
        ]

# Color Range Model
class ColorRange(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    color = models.CharField(max_length =10, 
                            choices = COLOR_RANGE_CHOICES, 
                            default=1, 
                            verbose_name="Color",
                            blank=False
                        )
    range = models.CharField(max_length = 20, 
                            verbose_name="Results Range",
                            default="",
                            blank=False
                            )
    
    def __str__(self):
        return "{user}--{color}--{range}".format(user=self.user.username, color=COLOR_RANGE_CHOICES[int(self.color)][1], range=self.range)


# Config Rules Model
class configurationRules(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    header = models.CharField(max_length=50,
                            verbose_name="Header Name ( or Category)",
                            blank=False,
                            default = '',
                            help_text="Header Name ( or Category) Unique Header or category name where group of \
                                        same stats will be displayed Linux Fruit Details DB Fruit Details Daily \
                                        Max Price Stats Etc…",
                            error_messages = {
                                'blank': "Header Name is required.",
                            })
    name = models.CharField(max_length=20,
                            verbose_name="Name",
                            blank=False,
                            default='',
                            help_text="Stats rules name",
                            error_messages = {
                                'blank': "Stats rules name is required"
                            })
    source = models.CharField(max_length=10,
                            choices = SOURCE_CHOICES,
                            verbose_name="Source",
                            default=1,
                            blank=False,
                            null=False,
                            help_text="Select source from which results are to be fetched",
                            error_messages = {
                                'blank': "Source is required",
                                'invalid': 'Invalid source choice'
                            })
    source_query = models.CharField(max_length=100,
                                    default='',
                                    verbose_name="SQL Query/Linux Shell Command",
                                    blank=False,
                                    help_text = "SQL Query or Linux shell command",
                                    error_messages = {
                                        'blank' : 'SQL Query/Linux Shell Command is required'
                                    })
    resultDataType = models.CharField(max_length=10,
                                    choices  =RESULTS_DATATYPE_CHOICES,
                                    default=4,
                                    verbose_name="Result Data Type",
                                    blank=False,
                                    help_text = "Results Data Type",
                                    error_messages = {
                                        'blank' : "Results Data Type  is requiured"
                                    })
    color = models.ManyToManyField(ColorRange)
    Schedule_Run_Config  = models.CharField(max_length=100,
                                        blank=True,
                                        verbose_name="Schedule Run Config",
                                        default=""
                                        )
    emailID = models.EmailField(max_length=30, 
                                verbose_name="Email",
                                blank=True,
                                default="",
                                help_text="Email id if incase scheduled run results need to be sent"
                                )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = models.Manager() # The default manager.
    configurations_rules_manager = ConfigurationRulesManager() # Our custom manager.
    
    def get_current_object_results(self):
        return self.configresultsdatabase_set.all()
    
    
    def __str__(self):
        return "{user}--Configuration Rules".format(user=self.user.username)

# Results Sections
class configResultsDataBase(models.Model):
    user = models.ForeignKey(get_user_model(),
                            on_delete=models.CASCADE)


    configRules = models.ForeignKey(configurationRules,
                                    on_delete=models.CASCADE)
    
    query_store_DB_1 = models.CharField(max_length=100,
                                    verbose_name="Query for DB 1",
                                    default = '',
                                    blank=False
                    )
    
    results_store_DB_1 = models.CharField(max_length=100,
                                    verbose_name="Results for DB 1",
                                    default = '',
                                    blank=False
                    )
    
    results_store_DB_1_timestamp = models.DateTimeField(verbose_name="Timestamp for DB 1",
                                                        default = timezone.now
                                )
    
    
    query_store_DB_2 = models.CharField(max_length=100,
                                verbose_name="Query for DB 2",
                                default = '',
                                blank=False
                        )
    
    results_store_DB_2 = models.CharField(max_length=100,
                                        verbose_name="Results for DB 2",
                                        default = '',
                                        blank=False
                        )
    
    results_store_DB_2_timestamp = models.DateTimeField(verbose_name="Timestamp for DB 2",
                                                        default = timezone.now
                                )
                                
    
    updated_timtstamp = models.DateTimeField(verbose_name="Results Updated Time",
                                             default = timezone.now
                                             )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return "{u}--{c}--{t}".format(
            u=self.user.username,
            t = self.timestamp,
            c = self.configRules.name
            )
    