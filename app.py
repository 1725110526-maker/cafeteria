from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Estructuras en memoria para recordar los datos durante las pruebas
cola_prioritaria = []
cola_normal = []
contador_pedidos = 1

estadisticas = {
    "total_atendidos": 0,
    "normales_atendidos": 0,
    "prioritarios_atendidos": 0,
    "tiempo_total": 0
}

@app.route('/')
def index():
    return render_template('index.html')

# API para obtener el estado actual de las filas y estadísticas
@app.route('/api/estado', methods=['GET'])
def obtener_estado():
    return jsonify({
        "cola_prioritaria": cola_prioritaria,
        "cola_normal": cola_normal,
        "estadisticas": estadisticas
    })

# Requerimiento 1: Registrar pedido
@app.route('/api/registrar', methods=['POST'])
def registrar_pedido():
    global contador_pedidos
    data = request.json
    
    nuevo_pedido = {
        "numero": contador_pedidos,
        "cliente": data.get("cliente"),
        "producto": data.get("producto"),
        "cantidad": int(data.get("cantidad", 1)),
        "tipo": data.get("tipo"),
        "tiempo": int(data.get("tiempo", 5))
    }
    
    contador_pedidos += 1
    
    if nuevo_pedido["tipo"] == "prioritario":
        cola_prioritaria.append(nuevo_pedido)
    else:
        cola_normal.append(nuevo_pedido)
        
    return jsonify({"success": True, "pedido": nuevo_pedido})

# Requerimiento 2: Preparar el siguiente pedido
@app.route('/api/preparar', methods=['POST'])
def preparar_pedido():
    pedido_atendido = None
    
    if cola_prioritaria:
        pedido_atendido = cola_prioritaria.pop(0)
        estadisticas["prioritarios_atendidos"] += 1
    elif cola_normal:
        pedido_atendido = cola_normal.pop(0)
        estadisticas["normales_atendidos"] += 1
        
    if pedido_atendido:
        estadisticas["total_atendidos"] += 1
        estadisticas["tiempo_total"] += pedido_atendido["tiempo"]
        return jsonify({"success": True, "pedido": pedido_atendido})
    
    return jsonify({"success": False, "message": "No hay pedidos pendientes."})

# Requerimiento 3: Consultar el siguiente pedido
@app.route('/api/siguiente', methods=['GET'])
def consultar_siguiente():
    if cola_prioritaria:
        return jsonify({"success": True, "pedido": cola_prioritaria[0], "fila": "Prioritaria"})
    elif cola_normal:
        return jsonify({"success": True, "pedido": cola_normal[0], "fila": "Normal"})
    return jsonify({"success": False, "message": "No hay pedidos en espera."})

# Requerimiento 6: Cancelar pedido
@app.route('/api/cancelar/<int:numero>', methods=['DELETE'])
def cancelar_pedido(numero):
    global cola_prioritaria, cola_normal
    
    encontrado = False
    # Buscar en prioritarios
    for p in cola_prioritaria:
        if p["numero"] == numero:
            cola_prioritaria.remove(p)
            encontrado = True
            break
            
    # Buscar en normales si no estaba en prioritarios
    if not encontrado:
        for p in cola_normal:
            if p["numero"] == numero:
                cola_normal.remove(p)
                encontrado = True
                break
                
    if encontrado:
        return jsonify({"success": True, "message": f"Pedido #{numero} cancelado."})
    return jsonify({"success": False, "message": "Pedido no encontrado."})

if __name__ == '__main__':
    app.run(debug=True)