class Evento:
    def __init__(self, nombre='', num_mesas=0, inv_por_mesa=0, fecha=None, cliente='', telefono='', id=None):
        self.id = id
        self.nombre = nombre
        self.num_mesas = int(num_mesas)
        self.inv_por_mesa = int(inv_por_mesa)
        self.fecha = fecha
        self.cliente = cliente
        self.telefono = telefono
        self.participantes = []  # lista de Participante
        self.asignaciones_mesas = []  # lista de dicts: [{'id':1,'capacidad':x,'invitados':[nombres]}]

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

    def to_android_json(self):
        """Genera la estructura JSON requerida por el proyecto Android."""
        # Creamos el mapa de participantes para acceso rápido
        parts_map = {p.nombre: p for p in self.participantes}
        
        resultado = []
        nombres_asignados = set()
        
        # 1. Procesamos las mesas existentes en asignaciones_mesas
        for mesa in self.asignaciones_mesas:
            m_id = mesa.get('id', 0)
            m_cap = mesa.get('capacidad', self.inv_por_mesa)
            m_invitados = mesa.get('invitados', [])
            
            mesa_json = {
                "numero": m_id,
                "capacidad": m_cap,
                "participantes": []
            }
            
            for nombre in m_invitados:
                p = parts_map.get(nombre)
                if p:
                    mesa_json["participantes"].append({
                        "nombre": p.nombre,
                        "prefiere": p.prefiere,
                        "noPrefiere": p.no_prefiere
                    })
                    nombres_asignados.add(nombre)
            
            resultado.append(mesa_json)
            
        # 2. Invitados sin asignar (Mesa 0)
        sin_asignar = [p for p in self.participantes if p.nombre not in nombres_asignados]
        if sin_asignar:
            mesa_0 = {
                "numero": 0,
                "capacidad": 0, # Opcional para mesa 0
                "participantes": [
                    {
                        "nombre": p.nombre,
                        "prefiere": p.prefiere,
                        "noPrefiere": p.no_prefiere
                    } for p in sin_asignar
                ]
            }
            resultado.append(mesa_0)
            
        return resultado
