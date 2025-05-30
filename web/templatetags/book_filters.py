from django import template
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

register = template.Library()

@register.filter
def add_years(date, years):
    """Add years to a date"""
    if not date:
        return datetime.now().date() + relativedelta(years=years)
    try:
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        return date + relativedelta(years=years)
    except:
        return datetime.now().date() + relativedelta(years=years)

@register.filter
def get_condition_schema(status):
    """Convert Have status to schema.org condition"""
    condition_map = {
        'new': 'http://schema.org/NewCondition',
        'used': 'http://schema.org/UsedCondition', 
        'damaged': 'http://schema.org/DamagedCondition'
    }
    return condition_map.get(status, 'http://schema.org/UsedCondition')

@register.filter
def get_availability_schema(is_available):
    """Convert availability to schema.org availability"""
    if is_available:
        return 'http://schema.org/InStock'
    else:
        return 'http://schema.org/OutOfStock'

@register.filter
def format_currency(value):
    """Format currency for schema.org"""
    return f"{value} POINTS"

@register.filter  
def future_date(years=1):
    """Get a future date by adding years to current date"""
    try:
        return (datetime.now().date() + relativedelta(years=int(years))).strftime('%Y-%m-%d')
    except:
        return (datetime.now().date() + relativedelta(years=1)).strftime('%Y-%m-%d')


