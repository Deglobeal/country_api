from django.db import models
from django.core.exceptions import ValidationError

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capital = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    estimated_gdp = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    flag_url = models.URLField(max_length=500, null=True, blank=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'countries'
        ordering = ['name']
    
    def clean(self):
        errors = {}
        
        # Required fields validation
        if not self.name:
            errors['name'] = 'is required'
        if not self.population:
            errors['population'] = 'is required'
        if self.population and self.population < 0:
            errors['population'] = 'must be non-negative'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name