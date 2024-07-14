import requests
import json

api_url = 'https://api.baselinker.com/connector.php'
headers = {
    'X-BLToken':
    '4001501-4005792-2NKT47Y31UN3ON9QJL9QGUX2E2STUKX4BKYI0UBCPV9FWL9722LWETMJVOYYJXAN'
}

order_source = 'allegro'
order_source_id_filter = 19336
order_status_id_filters = [129091, 129402]
exchange_rate = 4.30

def get_orders(date_confirmed_from, order_source, order_source_id_filter, order_status_id_filter):
    parameters = {
        'date_from': date_confirmed_from,
        'filter_order_source': order_source,
        'filter_order_source_id': order_source_id_filter,
        'status_id': order_status_id_filter,
        'get_unconfirmed_orders': False
    }
    data = {'method': 'getOrders', 'parameters': json.dumps(parameters)}
    response = requests.post(api_url, headers=headers, data=data)
    return response.json()

def get_inventory_products_data(inventory_id, product_ids):
    parameters = {'inventory_id': inventory_id, 'products': product_ids}
    data = {
        'method': 'getInventoryProductsData',
        'parameters': json.dumps(parameters)
    }
    response = requests.post(api_url, headers=headers, data=data)
    return response.json()

def calculate_net_income(orders, purchase_prices, exchange_rate):
    total_net_income = 0
    net_incomes = []

    for order in orders:
        net_income = 0
        for product in order["products"]:
            product_price_net = product["price_brutto"] / (1 + product["tax_rate"] / 100)
            purchase_price = (purchase_prices.get(str(product["product_id"]), 0) / exchange_rate) / (1 + product["tax_rate"] / 100)
            net_income += (product_price_net - purchase_price) * product["quantity"]

        delivery_net = order["delivery_price"] / (1 + 8 / 100)
        net_income += delivery_net

        net_incomes.append({
            "order_id": order["order_id"],
            "net_income": net_income
        })
        total_net_income += net_income

    return net_incomes, total_net_income

all_orders = []

for order_status_id_filter in order_status_id_filters:
    last_date_confirmed = 0
    while True:
        orders_response = get_orders(last_date_confirmed, order_source, order_source_id_filter, order_status_id_filter)

        if 'orders' in orders_response:
            orders = orders_response['orders']
            all_orders.extend(orders)

            if len(orders) < 100:
                break

            last_order_date_confirmed = int(orders[-1]['date_confirmed']) + 1
            last_date_confirmed = last_order_date_confirmed
        else:
            break

filtered_orders = []
for order in all_orders:
    date_confirmed = order['date_confirmed']
    if date_confirmed_from <= date_confirmed < date_confirmed_to and order['invoice_country_code'] == 'SK':
        filtered_orders.append(order)

if filtered_orders:
    product_ids = list(set(product['product_id'] for order in filtered_orders for product in order['products']))
    inventory_id = "58444"
    inventory_response = get_inventory_products_data(inventory_id, product_ids)
    inventory_products = inventory_response.get('products', {})

    purchase_prices = {str(pid): pdata['average_cost'] for pid, pdata in inventory_products.items()}

    net_incomes, total_net_income = calculate_net_income(filtered_orders, purchase_prices, exchange_rate)

    print("\nEUR Market:")
    for income in net_incomes:
        print(f"Order ID: {income['order_id']}, Net Income: {income['net_income']:.2f} EUR")

    print(f"Total Net Income: {total_net_income:.2f} EUR")
    print(f"Total Number of Orders: {len(filtered_orders)}")
else:
    print("Brak zamówień do przetworzenia.")
