from clases.cliente import Cliente


def main():
    print("Iniciando cliente...")
    cliente = Cliente()

    while True:
        print("\nAcciones disponibles:")
        print("1. Registrarse")
        print("2. Añadir pedido")
        print("3. Ver pedidos")
        print("4. Cancelar pedido")
        print("5. Salir")
        choice = input("Seleccione una opción: ")

        if choice == '1':
            nombre_usuario = input(
                "Ingrese el numbre de usuario a introducir: ")
            cliente.registrar(nombre_usuario)
        elif choice == '2':
            productos_ids = input(
                "Introduzca los ids de los productos a añadir en el pedido (separador por comas): ")
            cliente.realizar_pedido(productos_ids)
        elif choice == '3':
            cliente.ver_pedidos()
        elif choice == '4':
            pedido_id = input("Introduzca el id del pedido a cancelar: ")
            cliente.cancelar_pedido(pedido_id)
        elif choice == '5':
            break
        else:
            print("Opción no válida, intente de nuevo.")

    cliente.close()


if __name__ == '__main__':
    main()
