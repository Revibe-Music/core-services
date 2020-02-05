from django.utils.html import format_html

from revibe._helpers.symbols import CHECK_MARK, CROSS_MARK

# -----------------------------------------------------------------------------

def check_deletion(obj):
    # check = getattr(obj, 'is_deleted')
    # symbol = CROSS_MARK if check else CHECK_MARK
    # return format_html(
    #     "<span>{}</span>",
    #     symbol
    # )
    return html_check_x(obj, 'is_deleted', reverse=True)

def check_display(obj):
    # check = getattr(obj, 'is_displayed')
    # symbol = CHECK_MARK if check else CROSS_MARK
    # return format_html(
    #     "<span>{}</span>",
    #     symbol
    # )
    return html_check_x(obj, 'is_displayed')


def html_check_x(obj, attribute, reverse=False):
    check = getattr(obj, attribute)
    if not reverse:
        symbol = CHECK_MARK if check else CROSS_MARK
    else:
        symbol = CROSS_MARK if check else CHECK_MARK
    return format_html(
        "<span>{}</span>",
        symbol
    )
