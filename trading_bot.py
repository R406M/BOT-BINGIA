import ccxt

api_key = '6755e102c0ca880001264597'
api_secret = 'a1025f04-1bf2-41eb-a24f-9ee8088f5156'
api_passphrase = 'Ab27*7AS'

exchange = ccxt.kucoin({
    'apiKey': api_key,
    'secret': api_secret,
    'password': api_passphrase,
})

def ejecutar_orden(tipo, simbolo, cantidad):
    try:
        if tipo == 'compra':
            order = exchange.create_market_buy_order(simbolo, cantidad)
        elif tipo == 'venta':
            order = exchange.create_market_sell_order(simbolo, cantidad)
        print(f"Orden ejecutada: {order}")
    except Exception as e:
        print(f"Error al ejecutar la orden: {e}")
