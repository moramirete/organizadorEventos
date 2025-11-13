class Evento:
    def __init__(self, nombre='', num_mesas=0, inv_por_mesa=0, fecha=None, cliente='', telefono=''):
        self.nombre = nombre
        self.num_mesas = int(num_mesas)
        self.inv_por_mesa = int(inv_por_mesa)
        self.fecha = fecha
        self.cliente = cliente
        self.telefono = telefono
        self.participantes = []  # lista de Participante

    def agregar_participante(self, participante):
        self.participantes.append(participante)

    def eliminar_participante(self, index):
        if 0 <= index < len(self.participantes):
            self.participantes.pop(index)

    def contar_participantes(self):
        return len(self.participantes)

    def capacidad_total(self):
        # capacidad total calculada como num_mesas * inv_por_mesa
        return self.num_mesas * self.inv_por_mesa
