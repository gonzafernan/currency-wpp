import requests
from config import *

BASE_URL = "https://v6.exchangerate-api.com/v6/"


# Pair Conversion Requests
def pair_conversion(curr1, curr2, amount=0):
    url = BASE_URL + API_KEY + "/pair/" + curr1 + "/" + curr2
    if amount != 0:
        url = url + "/" + str(amount)
    r = requests.get(url).json()
    print(r)

    if r['result'] == 'success':
        if amount != 0:
            return r['conversion_result']
        return r['conversion_rate']
    else:
        return 0


if __name__ == '__main__':
    print(pair_conversion("COP", "ARS"))
