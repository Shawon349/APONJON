from django import template

register = template.Library()

ENG_TO_BN = {
    '0': '০',
    '1': '১',
    '2': '২',
    '3': '৩',
    '4': '৪',
    '5': '৫',
    '6': '৬',
    '7': '৭',
    '8': '৮',
    '9': '৯',
}

@register.filter(name='bn_num')
def bn_num(value):
    """
    Converts English numerals in numbers or strings into Bengali numerals.
    Usage: {{ total_reported|bn_num }} -> ৩
    """
    if value is None:
        return '০'
    val_str = str(value)
    return ''.join(ENG_TO_BN.get(ch, ch) for ch in val_str)
