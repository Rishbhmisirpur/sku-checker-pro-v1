import re

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()


def clean_price(text):
    try:
        return round(float(re.sub(r'[^0-9.]', '', str(text))), 2)
    except:
        return 0.0
