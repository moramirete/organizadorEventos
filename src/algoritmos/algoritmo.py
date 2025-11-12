from ortools.sat.python import cp_model
from typing import List, Dict, Tuple, Optional

class Persona:
    """Clase para representar a un participante con sus relaciones."""
    def __init__(self, nombre: str, amistades: Optional[List[str]] = None, enemistades: Optional[List[str]] = None):
        self.nombre = nombre
        self.amistades = amistades or []
        self.enemistades = enemistades or []
    
    def __repr__(self):
        return self.nombre

# --- Datos de Ejemplo ---
personas = [
    Persona("Ana", amistades=["Luis"]),
    Persona("Luis", amistades=["Ana", "Sofía"]),
    Persona("Marta", enemistades=["Pedro"]),
    Persona("Pedro", enemistades=["Marta"]),
    Persona("Sofía", amistades=["Luis"], enemistades=["Marta"]),
]

# ----------------------------------------------------------------------
# FUNCIONES AUXILIARES PARA EL ALGORITMO DE OPTIMIZACIÓN
# ----------------------------------------------------------------------

def get_constraints_count(participantes: List[Persona]) -> Dict[str, int]:
    """Calcula el número total de restricciones por persona para la heurística de eliminación."""
    count = {}
    nombres_actuales = {p.nombre for p in participantes}
    for p in participantes:
        count[p.nombre] = 0
        # Amistades (Must be together)
        for amigo in p.amistades:
            if amigo in nombres_actuales:
                count[p.nombre] += 1
        # Enemistades (Must be separate)
        for enemigo in p.enemistades:
            if enemigo in nombres_actuales:
                count[p.nombre] += 1
    return count

def solve_subproblem(participantes: List[Persona], tamano_mesa: int) -> Optional[Dict[str, int]]:
    """Intenta resolver el subproblema con el conjunto actual de participantes."""
    model = cp_model.CpModel()
    nombres = [p.nombre for p in participantes]
    
    if not nombres:
        return {}
    
    # Calcular el número mínimo de mesas necesarias.
    num_mesas = len(participantes) // tamano_mesa
    if len(participantes) % tamano_mesa != 0:
         num_mesas += 1
    num_mesas = max(1, num_mesas) # Asegurar al menos 1 mesa si hay gente

    # 1. Variables: mesa asignada a cada persona
    mesas = {
        nombre: model.NewIntVar(0, num_mesas - 1, nombre)
        for nombre in nombres
    }
    
    # 2. Restricciones de Amistad y Enemistad
    nombres_set = set(nombres)
    for p in participantes:
        for amigo in p.amistades:
            if amigo in nombres_set:
                model.Add(mesas[p.nombre] == mesas[amigo])
        for enemigo in p.enemistades:
            if enemigo in nombres_set:
                model.Add(mesas[p.nombre] != mesas[enemigo])

    # 3. Restricción de tamaño máximo por mesa
    for m in range(num_mesas):
        indicators = []
        for nombre in nombres:
            b = model.NewBoolVar(f"{nombre}_en_mesa_{m}")
            # Si mesa[nombre] == m, entonces b = 1
            model.Add(mesas[nombre] == m).OnlyEnforceIf(b)
            model.Add(mesas[nombre] != m).OnlyEnforceIf(b.Not())
            indicators.append(b)
        model.Add(sum(indicators) <= tamano_mesa)

    # 4. Resolver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0 
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {nombre: solver.Value(mesas[nombre]) for nombre in nombres}
    else:
        return None

# ----------------------------------------------------------------------
# FUNCIÓN PRINCIPAL SOLUCIÓN ITERATIVA
# ----------------------------------------------------------------------

def asignar_mesas_optimizando(participantes: List[Persona], tamano_mesa: int) -> Tuple[Optional[Dict[str, int]], List[str]]:
    """
    Intenta asignar mesas. Si falla, elimina iterativamente a la persona 
    más restringida hasta encontrar una solución factible.
    Devuelve: (Solución de mesas, Lista de nombres excluidos)
    """
    
    participantes_restantes = list(participantes)
    personas_excluidas: List[str] = []
    solucion: Optional[Dict[str, int]] = None
    
    # Bucle de relajación: se ejecuta mientras no haya solución y queden personas
    while solucion is None and participantes_restantes:
        
        # Intenta resolver con el subconjunto actual de personas
        solucion = solve_subproblem(participantes_restantes, tamano_mesa)

        if solucion is not None:
            break
            
        # Si falla (solucion is None), identifica y elimina al candidato.
        
        # 1. Heurística: Encontrar a la persona con más restricciones
        contadores = get_constraints_count(participantes_restantes)
        
        candidato_a_excluir = None
        max_restricciones = -1
        
        for p in participantes_restantes:
            if contadores[p.nombre] > max_restricciones:
                max_restricciones = contadores[p.nombre]
                candidato_a_excluir = p

        # 2. Excluir y reintentar
        if candidato_a_excluir:
            print(f"-> Inviable. Excluyendo a: {candidato_a_excluir.nombre} (Restricciones activas: {max_restricciones})")
            participantes_restantes.remove(candidato_a_excluir)
            personas_excluidas.append(candidato_a_excluir.nombre)
        else:
            # Esto solo debería ocurrir si la lista está vacía, 
            # pero el bucle ya maneja eso.
            break

    return solucion, personas_excluidas

# ----------------------------------------------------------------------
# RESULTADO FINAL
# ----------------------------------------------------------------------

# El problema original es Inviable, ya que (Ana, Luis, Sofía) deben ir juntos (3 personas), 
# pero luego Marta y Pedro quedan como los únicos restantes (2 personas), y deben ir 
# separados entre sí y de Sofía, lo que fuerza a Pedro a la mesa de Ana/Luis/Sofía, 
# violando el tamaño máximo de 3.
sol, excluidos = asignar_mesas_optimizando(personas, tamano_mesa=3)

print(f"\nIntentando asignar mesas (Tamaño máximo: 3)...")

if sol is not None:
    
    # Formatear la salida para mostrar las mesas
    mesas_final = {}
    for nombre, mesa_id in sol.items():
        if mesa_id not in mesas_final:
            mesas_final[mesa_id] = []
        mesas_final[mesa_id].append(nombre)
        
    print("\n✅ Solución Factible Encontrada:")
    print("------------------------------")
    
    print("Asignación de Mesas:")
    for mesa_id, nombres_mesa in sorted(mesas_final.items()):
        print(f"  Mesa {mesa_id}: {', '.join(nombres_mesa)}")

    if excluidos:
        print(f"\n🚫 Personas Excluidas para encontrar Factibilidad:")
        print(f"  {', '.join(excluidos)}")
    else:
        print("\n🎉 Todas las personas fueron asignadas sin conflictos.")
else:
    print("\n❌ No se pudo encontrar una solución factible, incluso después de excluir a todos los candidatos principales.")
    print(f"Personas Excluidas: {', '.join(excluidos)}")