import socket
import select

# Создание неблокирующего UDP сокета
node_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
node_socket.setblocking(0)

# Адрес и порт, на котором будет прослушиваться UDP пакеты
server_address = ('localhost', 12345)
node_socket.bind(server_address)

# Словарь, где ключом является адрес, а значением - соответствующий сокет
connection_map = {}
# Словарь, где ключом является сокет, а значением - соответствующий адрес
connection_map_reversed = {}

while True:
    # Ожидание получения UDP пакета
    ready_sockets, _, _ = select.select([node_socket] + list(connection_map.keys()), [], [])
    
    for sock in ready_sockets:
        if sock is node_socket:
            # Пришел новый UDP пакет
            data, address = node_socket.recvfrom(1024)
            print(f"Received packet from: {address}")
            
            if address in connection_map:
                # Пересылаем пакет на соответствующий сокет
                destination_socket = connection_map[address]
                destination_socket.send(data)
            
            else:
                # Открываем новый неблокирующий сокет для данного адреса
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                new_socket.setblocking(0)
                new_socket.bind((address[0], 0))
                
                # Добавляем соответствия в connection_map и connection_map_reversed
                connection_map[address] = new_socket
                connection_map_reversed[new_socket] = address
                print(f"Opened new socket for address: {address}")
        
        else:
            # Пришел пакет от уже открытого сокета
            data, _ = sock.recvfrom(1024)
            destination_address = connection_map_reversed[sock]
            print(f"Received packet from node: {destination_address}")
            
            # Шлем пакет обратно на адрес
            node_socket.sendto(data, destination_address)
