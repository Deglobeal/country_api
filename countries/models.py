from django.db import models
from django.core.exceptions import ValidationError
import random

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capital = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, blank=True, null=True)
    exchange_rate = models.FloatField(null=True, blank=True)
    estimated_gdp = models.FloatField(null=True, blank=True)
    flag_url = models.URLField(blank=True, null=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)

    def clean(self):
        errors = {}
        
        if not self.name:
            errors['name'] = 'is required'
        if self.population is None:
            errors['population'] = 'is required'
        if not self.currency_code:
            errors['currency_code'] = 'is required'
            
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        
        # Calculate estimated_gdp if we have the required data
        if (self.population and self.exchange_rate and 
            self.exchange_rate > 0 and self.currency_code):
            random_multiplier = random.uniform(1000, 2000)
            self.estimated_gdp = (self.population * random_multiplier) / self.exchange_rate
        else:
            self.estimated_gdp = None
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'countries'
        ordering = ['name']