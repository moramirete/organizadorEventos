from typing import List, Dict, Tuple, Optional

class Persona:
    """Clase para representar a un participante con sus relaciones."""
    def __init__(self, nombre: str, amistades: Optional[List[str]] = None, enemistades: Optional[List[str]] = None):
        self.nombre = nombre
        self.amistades = [a.strip() for a in (amistades or []) if a.strip()]
        self.enemistades = [e.strip() for e in (enemistades or []) if e.strip()]
    
    def __repr__(self):
        return self.nombre

def asignar_mesas_optimizando(participantes: List[Persona], tamano_mesa: int) -> Tuple[Optional[Dict[str, int]], List[str], Dict[str, int]]:
    """
    Asigna mesas buscando el óptimo global de satisfacción.
    Versión Pure-Python (sin dependencias de ortools).
    Devuelve: (Asignación, Excluidos, Metricas_Satisfaccion)
    """
    if not participantes:
        return {}, [], {"total": 0, "cumplidos": 0}

    # 1. Normalización y Estructura de Datos
    canonical_to_original = {p.nombre.strip().lower(): p.nombre for p in participantes}
    nombres_canonicos = list(canonical_to_original.keys())
    
    # Mapas de relaciones (en minúsculas)
    amigos_map = {p.nombre.strip().lower(): [a.lower() for a in p.amistades] for p in participantes}
    enemigos_map = {p.nombre.strip().lower(): [e.lower() for e in p.enemistades] for p in participantes}

    num_participantes = len(nombres_canonicos)
    num_mesas = (num_participantes + tamano_mesa - 1) // tamano_mesa
    num_mesas = max(1, num_mesas)

    # 2. Algoritmo Greedy con Heurística de Satisfacción
    # Inicializamos mesas vacías
    mesas_data = [[] for _ in range(num_mesas)]
    asignacion = {} # nombre_canon -> mesa_index
    
    # Ordenamos a los participantes por "importancia" (quienes tienen más restricciones/deseos van primero)
    def calcular_peso(nombre):
        return len(amigos_map.get(nombre, [])) + len(enemigos_map.get(nombre, []))
    
    participantes_ordenados = sorted(nombres_canonicos, key=calcular_peso, reverse=True)

    for p in participantes_ordenados:
        best_mesa = -1
        max_score = -1000 # Puntuación de "felicidad" si va en esa mesa
        
        for m_idx in range(num_mesas):
            # A. Comprobar Hard Constraints
            # 1. Capacidad
            if len(mesas_data[m_idx]) >= tamano_mesa:
                continue
            
            # 2. Enemistades (HARD)
            es_viable = True
            for otro in mesas_data[m_idx]:
                if otro in enemigos_map.get(p, []) or p in enemigos_map.get(otro, []):
                    es_viable = False
                    break
            if not es_viable:
                continue
            
            # B. Calcular Satisfacción (SOFT)
            score = 0
            for otro in mesas_data[m_idx]:
                # Si p quiere estar con 'otro'
                if otro in amigos_map.get(p, []):
                    score += 10
                # Si 'otro' quiere estar con p
                if p in amigos_map.get(otro, []):
                    score += 10
            
            # Preferimos mesas más llenas si hay empate de score? No, mejor coger la primera.
            if score > max_score:
                max_score = score
                best_mesa = m_idx
        
        if best_mesa != -1:
            mesas_data[best_mesa].append(p)
            asignacion[p] = best_mesa

    # 3. Cálculo de métricas de satisfacción
    total_deseos = 0
    deseos_cumplidos = 0
    for p_canon, mesa_idx in asignacion.items():
        for amigo in amigos_map.get(p_canon, []):
            if amigo in nombres_canonicos:
                total_deseos += 1
                if asignacion.get(amigo) == mesa_idx:
                    deseos_cumplidos += 1
    
    metricas = {"total": total_deseos, "cumplidos": deseos_cumplidos}

    # 4. Formatear Resultado Final (usando nombres originales)
    resultado = {}
    excluidos = []
    for p in nombres_canonicos:
        if p in asignacion:
            resultado[canonical_to_original[p]] = asignacion[p]
        else:
            excluidos.append(canonical_to_original[p])

    if not resultado and participantes:
        return None, ["No se encontró ninguna asignación válida"], metricas

    return resultado, excluidos, metricas

# --- Pruebas del Caso del Usuario (Versión Pure Python) ---
if __name__ == "__main__":
    test_personas = [
        Persona("Figuel", amistades=["novia"]),
        Persona("Novia", amistades=["Figel"], enemistades=["exnovio"]),
        Persona("Exnovio", amistades=["Novia"]),
    ]

    print("\nResultados de la prueba (Figuel, Novia, Exnovio) - SIN ORTOOLS:")
    print("Mesa de 2 personas:")
    sol, excluidos, metricas = asignar_mesas_optimizando(test_personas, tamano_mesa=2)

    if sol:
        mesas_res = {}
        for n, m in sol.items():
            mesas_res.setdefault(m, []).append(n)
        for m_id, gente in sorted(mesas_res.items()):
            print(f"  Mesa {m_id+1}: {', '.join(gente)}")
        print(f"\nSatisfacción: {metricas['cumplidos']}/{metricas['total']} deseos cumplidos.")
    else:
        print("  No se encontró solución.")
