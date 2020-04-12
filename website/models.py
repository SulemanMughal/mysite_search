from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

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
