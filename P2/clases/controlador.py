import pika
import pickle
import uuid
from .config import RABBITMQ_SERVER
from .robot import Robot
from .repartidor import Repartidor
from .cliente import Cliente
from .pedido import Pedido


class Controlador:
    def __init__(self):
        self.clientes = {}
        self.pedidos = []

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_SERVER))
        self.channel = self.connection.channel()

        self.channel.queue_declare(
            queue='2323_04_controlador_robots_produccion', durable=False, auto_delete=True)
        self.channel.queue_declare(
            queue='2323_04_controlador_robots_consumo', durable=False, auto_delete=True)

        self.channel.queue_declare(
            queue='2323_04_controlador_repartidores_produccion', durable=False, auto_delete=True)
        self.channel.queue_declare(
            queue='2323_04_controlador_repartidores_consumo', durable=False, auto_delete=True)

        self.channel.queue_declare(
            queue='2323_04_controlador_clientes', durable=False, auto_delete=True)

    def iniciar_controlador(self):
        self.channel.basic_consume(
            queue='2323_04_controlador_clientes', on_message_callback=self.cliente_callback)
        print("Esperando peticion RPC de los clientes...")

        self.channel.basic_consume(queue='2323_04_controlador_robots_consumo',
                                   on_message_callback=self.robots_callback,
                                   auto_ack=True)
        print("Esperando resultados de los robots...")

        self.channel.basic_consume(queue='2323_04_controlador_repartidores_consumo',
                                   on_message_callback=self.repartidores_callback,
                                   auto_ack=True)
        print("Esperando resultados de los repartidores...")

        self.channel.start_consuming()

    def get_cliente_uuid(self, nombre_usuario):
        if self.clientes.get(nombre_usuario) != None:
            return None

        return str(uuid.uuid4())

    def get_pedido_por_id(self, pedido_id):
        for pedido in self.pedidos:
            if pedido.pedido_id == pedido_id:
                return pedido

        return None

    def repartidores_callback(self, ch, method, props, body):
        body = body.decode('utf-8')

        if body.find('EN_ENTREGA') != -1:
            pedido_id = body[11:]
            pedido = self.get_pedido_por_id(pedido_id)
            if pedido is None:
                return

            print(body)
            pedido.actualizar_estado('En entrega')
            return

        print(body)
        if body.find('NO_ENTREGADO') != -1:
            pedido_id = body[13:]
            pedido = self.get_pedido_por_id(pedido_id)
            if pedido is None:
                return

            pedido.actualizar_estado('En cinta')
            self.asignar_repartidor(pedido_id)
            return

        pedido_id = body[10:]

        pedido = self.get_pedido_por_id(pedido_id)
        if pedido is None:
            return

        pedido.actualizar_estado('Entregado')

    def robots_callback(self, ch, method, props, body):
        body = body.decode('utf-8')
        print(body)

        if body.find('NO_MOVIDO') != -1:
            self.asignar_robot(body[10:])
            return

        pedido_id = body[7:]

        pedido = self.get_pedido_por_id(pedido_id)
        if pedido is None:
            return

        pedido.actualizar_estado('En cinta')
        self.asignar_repartidor(pedido_id)

    def cliente_callback(self, ch, method, props, body):
        # Hay que decodificar a formato de string sino no funciona
        body = body.decode('utf-8')

        print(body)
        if body.find("REGISTRAR") != -1:
            response = self.registrar_cliente(body)
        elif body.find("REALIZAR_PEDIDO") != -1:
            response = self.realizar_pedido(body)
        elif body.find("VER_PEDIDOS") != -1:
            response = self.mostrar_pedidos(body)
        elif body.find("CANCELAR_PEDIDO") != -1:
            response = self.cancelar_pedido(body)
        else:
            return

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(
                             correlation_id=props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def registrar_cliente(self, body):
        nombre_usuario = body[26:].strip()

        cliente_id = self.get_cliente_uuid(nombre_usuario)
        if cliente_id is None:
            response = f"REGISTRAR ERROR"
        else:
            response = f"REGISTRADO nombre_usuario: {nombre_usuario} cliente_id: {cliente_id}"
            self.clientes[nombre_usuario] = cliente_id

        return response

    def realizar_pedido(self, body):
        inicio_cliente_id = body.find("cliente_id: ") + len("cliente_id: ")
        fin_cliente_id = body.find(" productos_ids: ")
        cliente_id = body[inicio_cliente_id: fin_cliente_id].strip()

        inicio_productos_ids = body.find(
            "productos_ids: ") + len("productos_ids: ")
        productos_ids = body[inicio_productos_ids:].strip().split(',')

        new_pedido = Pedido(cliente_id, productos_ids)
        self.pedidos.append(new_pedido)

        response = f"PEDIDO_REALIZADO {new_pedido.pedido_id}"

        self.asignar_robot(new_pedido.pedido_id)
        return response

    def mostrar_pedidos(self, body):
        pedidos_ids = [id.strip() for id in body[12:].strip(
            "[]' ").replace("'", "").split(',')]

        response = "MOSTRAR_PEDIDOS "
        detalles_pedidos = []

        for id in pedidos_ids:
            pedido = self.get_pedido_por_id(id)
            if pedido != None:
                detalles_pedidos.append(pedido.__str__())

        if detalles_pedidos:
            response += ', '.join(detalles_pedidos)
        else:
            response += "ERROR no se han encontrado pedidos del cliente."

        return response

    def cancelar_pedido(self, body):
        pedido_id = body[16:].strip()

        pedido = self.get_pedido_por_id(pedido_id)
        if pedido is None:
            return f"CANCELAR_PEDIDO ERROR {pedido_id}"

        if pedido.cancelar():
            return f"PEDIDO_CANCELADO {pedido_id}"
        else:
            return f"CANCELAR_PEDIDO ERROR no se puede cancelar el pedido {pedido_id} en estado {pedido.status}."

    def asignar_robot(self, pedido_id):
        body_msg = f"MUEVE {pedido_id}"

        self.channel.basic_publish(
            exchange='',
            routing_key='2323_04_controlador_robots_produccion',
            body=body_msg,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            ))

    def asignar_repartidor(self, pedido_id):
        body_msg = f"ENTREGA {pedido_id}"

        self.channel.basic_publish(
            exchange='',
            routing_key='2323_04_controlador_repartidores_produccion',
            body=body_msg,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            ))

    def guardar_estado(self):
        with open('state.pkl', 'wb') as f:
            pickle.dump((self.clientes, self.pedidos), f)

    def cargar_estado(self):
        try:
            with open('state.pkl', 'rb') as f:
                self.clientes, self.pedidos = pickle.load(f)
        except FileNotFoundError:
            self.clientes = {}
            self.pedidos = []

    def close(self):
        self.channel.close()
        self.connection.close()

    def __str__(self):
        pedidos = " "
        for pedido in self.pedidos:
            pedidos += pedido.__str__()
            pedidos += "\n"

        if (pedidos == " "):
            pedidos = "No hay pedidos realizados"

        return f"Clientes: {self.clientes}\n Pedidos: {pedidos} "
