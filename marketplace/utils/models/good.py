"""
Created: 20 Mar. 2020
Author: Jordan Prechac
"""

# -----------------------------------------------------------------------------

def discounted_price(price, discount):
    """
    Takes in a price and a discount to return the discounted price

    Arguments
    ---------
    price: (int) Price
    discount: (float)

    Examples
    --------
    >>> discounted_price(100, 15)
    85.00
    """
    return round(float(price) * ((100 - float(discount)) / 100), 2)
