def classify_result(sku_ok, seller_ok, price_ok):
    if not sku_ok:
        return "SKU Wrong"
    elif not seller_ok:
        return "Seller Wrong"
    elif not price_ok:
        return "Price Wrong"
    return "Correct"
