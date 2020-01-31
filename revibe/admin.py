from django.utils.html import format_html

from revibe._helpers.symbols import CHECK_MARK, CROSS_MARK

# -----------------------------------------------------------------------------

def check_deletion(obj):
    check = getattr(obj, 'is_deleted')
    symbol = CROSS_MARK if check else CHECK_MARK
    return format_html(
        "<span>{}</span>",
        symbol
    )

def check_display(obj):
    check = getattr(obj, 'is_displayed')
    symbol = CHECK_MARK if check else CROSS_MARK
    return format_html(
        "<span>{}</span>",
        symbol
    )
