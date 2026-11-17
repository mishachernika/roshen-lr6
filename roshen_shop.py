def calc_discount(total, is_member):
    if total >= 1000:
        rate = 0.10
    elif total >= 500:
        rate = 0.05
    else:
        rate = 0.0
    if is_member:
        rate = rate + 0.03
    return round(total * (1 - rate), 2)


def process_order(order, stock, prices, is_member):
    total = 0
    for name in order:
        if name not in stock:
            return None
        if stock[name] < order[name]:
            return None
        if order[name] <= 0:
            return None                      # D-01, D-02: кількість має бути додатною
        total = total + prices[name] * order[name]
    final = calc_discount(total, is_member)
    for name in order:
        stock[name] = stock[name] - order[name]
    return final


def main():
    prices = {"Конфети": 120, "Торт": 190, "Шоколад": 85}
    stock = {"Конфети": 50, "Торт": 20, "Шоколад": 100}
    order = {"Конфети": 3, "Торт": 2}
    final = process_order(order, stock, prices, True)
    if final is None:
        print("Замовлення відхилено")
    else:
        print("До сплати:", final)


main()
