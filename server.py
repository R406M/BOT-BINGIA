from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Señal recibida: {data}")
    if data['action'] == 'compra':
        ejecutar_orden('compra', data['symbol'], data['amount'])
    elif data['action'] == 'venta':
        ejecutar_orden('venta', data['symbol'], data['amount'])
    return "OK"

if __name__ == "__main__":
    app.run(port=5000)
