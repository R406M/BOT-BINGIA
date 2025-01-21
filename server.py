import os
import logging
from flask import Flask, request, jsonify
import ccxt
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cargar las variables de entorno
load_dotenv()

# Cargar credenciales de API desde variables de entorno
api_key = os.getenv('KUCOIN_API_KEY')
api_secret = os.getenv('KUCOIN_API_SECRET')
api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')

# Verificar que las credenciales estén configuradas
if not api_key or not api_secret or not api_passphrase:
    logger.error("Las credenciales de API de KuCoin no están configuradas")
    raise Exception("Las credenciales de API de KuCoin no están configuradas")

# Configuración de la conexión a KuCoin usando ccxt
exchange = ccxt.kucoin({
    'apiKey': api_key,
    'secret': api_secret,
    'password': api_passphrase,
})

# Manejador de órdenes abiertas
orden_abierta = None

def obtener_saldo_moneda(moneda):
    balance = exchange.fetch_balance()
    return balance['total'][moneda]

def calcular_monto_operacion(moneda, porcentaje=85):
    saldo_total = obtener_saldo_moneda(moneda)
    return saldo_total * (porcentaje / 100)

def ejecutar_orden(tipo, simbolo, cantidad, tp_pct, sl_pct):
    try:
        if tipo == 'compra':
            order = exchange.create_market_buy_order(simbolo, cantidad)
        elif tipo == 'venta':
            order = exchange.create_market_sell_order(simbolo, cantidad)

        logger.info(f"Orden ejecutada: {order}")

        # Calcular TP y SL
        precio_entrada = order['price']
        tp = precio_entrada * (1 + tp_pct / 100)
        sl = precio_entrada * (1 - sl_pct / 100)

        return order, tp, sl
    except Exception as e:
        logger.error(f"Error al ejecutar la orden: {e}")
        return None, None, None

def cerrar_orden(orden):
    try:
        # Implementar lógica para cerrar la orden abierta
        # (dependiendo del tipo de orden y las herramientas disponibles)
        logger.info(f"Cerrando orden: {orden}")
        return True
    except Exception as e:
        logger.error(f"Error al cerrar la orden: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    global orden_abierta

    data = request.json
    logger.info(f"Señal recibida: {data}")

    # Validar los datos recibidos
    if not data or 'action' not in data or 'symbol' not in data or 'amount' not in data:
        logger.error("Datos de webhook incompletos o inválidos")
        return jsonify({"error": "Datos de webhook incompletos o inválidos"}), 400

    action = data['action']
    symbol = data['symbol']
    amount = data['amount']

    # Definir TP y SL en términos porcentuales
    tp_pct = 0.10  # Take profit en porcentaje
    sl_pct = 0.50  # Stop loss en porcentaje

    # Verificar si hay una operación abierta y cerrarla si es necesario
    if orden_abierta:
        logger.info("Cerrando operación anterior")
        if not cerrar_orden(orden_abierta):
            return jsonify({"status": "error", "message": "No se pudo cerrar la orden anterior"}), 500

    # Calcular monto de operación
    moneda_base, moneda_cotizada = symbol.split('/')
    cantidad_operar = calcular_monto_operacion(moneda_cotizada if action == 'compra' else moneda_base)

    # Ejecutar la orden
    orden_abierta, tp, sl = ejecutar_orden(action, symbol, cantidad_operar, tp_pct, sl_pct)
    if orden_abierta:
        # Aquí podrías añadir lógica para gestionar TP y SL, como monitorear el mercado o usar órdenes limit
        return jsonify({"status": "success", "order": orden_abierta, "tp": tp, "sl": sl})
    else:
        return jsonify({"status": "error", "message": "No se pudo ejecutar la orden"}), 500

if __name__ == "__main__":
    # Establecer puerto 5000 para desarrollo local
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)
