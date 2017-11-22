import sys
sys.path.insert(0,'../Tokens')

from coinbase_api_token import get_api

class PriceCollector:
    def __init__(self):
        self.api = get_api()

    def get_current_price(self):
        currency_code = 'USD'  # can also use EUR, CAD, etc.

        # Make the request
        price = self.api.get_spot_price(currency=currency_code)

        print 'Current bitcoin price in %s: %s' % (currency_code, price.amount)
        return price.amount