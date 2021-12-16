from django.utils.deconstruct import deconstructible
from django.core.validators import BaseValidator
from datetime import date

def calculate_age(born):
    today = date.today()
    return today.year - born.year - \
           ((today.month, today.day) < (born.month, born.day))

@deconstructible
class MinAgeValidator(BaseValidator):
    message = "Age must be at least %(limit_value)d."
    code = 'min_age'

    def compare(self, date, years):
        return calculate_age(date) < years