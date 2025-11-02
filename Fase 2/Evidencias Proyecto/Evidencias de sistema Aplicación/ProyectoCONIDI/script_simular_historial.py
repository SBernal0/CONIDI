# script_simular_historial.py
import os
import django
import random
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from faker import Faker

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
django.setup()

from control.models import Nino, Control, VacunaAplicada, CategoriaAlergia, RegistroAlergias
from login.models import Profesional

# Inicializar Faker
fake = Faker('es_CL')

print("Iniciando simulación de historiales clínicos REALISTAS (v4 con Perfiles)...")

# --- CONFIGURACIÓN DE LA SIMULACIÓN ---
HOY = date.today()
# se definen los perfiles de cumplimiento
PERFIL_CUMPLIDOR = 0.70  # 70% de los niños
PERFIL_OLVIDADIZO = 0.20 # 20% de los niños
# El 10% restante será "Caso de Riesgo / No Adherente"

# --- Obtenemos un profesional para firmar los registros ---
profesional_a_cargo = Profesional.objects.first()
if not profesional_a_cargo:
    print("Error: No se encontró ningún profesional en la BD. Registra uno primero.")
    exit()

print(f"Fecha de simulación: {HOY.strftime('%d/%m/%Y')}")
print(f"Profesional a cargo: {profesional_a_cargo.nombre_completo}")

# Listas para operaciones en bloque
controles_a_actualizar = []
vacunas_a_actualizar = []
ninos_a_actualizar_estado = []
alergias_a_crear = []

# Obtenemos todos los niños y categorías de alergia
todos_los_ninos = list(Nino.objects.all())
categorias_alergia = list(CategoriaAlergia.objects.all())

if not categorias_alergia:
    print("Advertencia: No hay categorías de alergia. Ejecuta 'script_poblar_categorias_alergia.py' primero.")
    
# --- FUNCIÓN DE CRECIMIENTO REALISTA (SIN CAMBIOS) ---
def get_realistic_growth(meses):
    if meses <= 12:
        peso_base = 3.5 + (meses * 0.7)
        talla_base = 50 + (meses * 2.5)
    else:
        meses_despues_del_ano = meses - 12
        peso_base = 11.9 + (meses_despues_del_ano * 0.21)
        talla_base = 80 + (meses_despues_del_ano * 0.5)
    
    peso = round(peso_base + random.uniform(-0.5, 0.5), 1)
    talla = round(talla_base + random.uniform(-1.0, 1.0), 1)
    pc = round(35 + (min(meses, 36) * 0.4), 1)
    
    return peso, talla, pc

# --- 1. PROCESAMOS A TODOS LOS NIÑOS ---
for nino in todos_los_ninos:
    
    # --- 1.A. Actualizar Estado de Seguimiento del Niño (por edad) ---
    edad_en_meses = (HOY.year - nino.fecha_nacimiento.year) * 12 + (HOY.month - nino.fecha_nacimiento.month)
    
    if edad_en_meses > 108 and nino.estado_seguimiento == 'ACTIVO': # Mayor de 9 años
        nino.estado_seguimiento = 'COMPLETADO'
        ninos_a_actualizar_estado.append(nino)
    
    # Asignamos un perfil de cumplimiento al niño
    perfil_chance = random.random()
    
    # Obtenemos todos los controles y vacunas pasados y pendientes del niño
    controles_pasados = nino.controles.filter(fecha_control_programada__lt=HOY, fecha_realizacion_control__isnull=True, deshabilitado=False).order_by('fecha_control_programada')
    vacunas_pasadas = nino.vacunas_aplicadas.filter(fecha_programada__lt=HOY, fecha_aplicacion__isnull=True, deshabilitado=False).order_by('fecha_programada')
    
    # --- 1.B. LÓGICA DE PERFILES DE CUMPLIMIENTO ---

    # --- PERFIL: CUMPLIDOR (70%) ---
    if perfil_chance < PERFIL_CUMPLIDOR:
        # Este niño hizo todo a tiempo.
        for control in controles_pasados:
            control.estado_control = 'Realizado'
            control.fecha_realizacion_control = control.fecha_control_programada + timedelta(days=random.randint(0, 5)) # Muy puntual
            
            meses_del_control = control.periodo.mes_control
            peso, talla, pc = get_realistic_growth(meses_del_control)
            
            control.pesokg = peso
            control.talla_cm = talla
            control.pc_cm = pc
            if control.talla_cm > 0:
                control.imc = round(control.pesokg / ((control.talla_cm / 100) ** 2), 2)
            
            control.calificacion_nutricional = 'Normal'
            control.calificacion_estatural = 'normal'
            control.profesional = profesional_a_cargo
            controles_a_actualizar.append(control)

        for vacuna_app in vacunas_pasadas:
            vacuna_app.fecha_aplicacion = vacuna_app.fecha_programada + timedelta(days=random.randint(0, 5))
            vacuna_app.dosis = "Dosis según PNI"
            vacuna_app.lugar = "CESFAM Hualpén"
            vacuna_app.profesional = profesional_a_cargo
            vacunas_a_actualizar.append(vacuna_app)

    # --- PERFIL: OLVIDADIZO (20%) ---
    elif perfil_chance < PERFIL_CUMPLIDOR + PERFIL_OLVIDADIZO:
        # Este niño se saltó 2 o 3 controles/vacunas
        controles_a_saltar = random.sample(list(controles_pasados), k=min(len(controles_pasados), random.randint(2, 3)))
        
        for control in controles_pasados:
            if control in controles_a_saltar:
                # No hacemos nada, este control queda pendiente y se mostrará en Alerta Roja
                pass
            else:
                # Realizó el resto de controles
                control.estado_control = 'Realizado'
                control.fecha_realizacion_control = control.fecha_control_programada + timedelta(days=random.randint(5, 20)) # Un poco más tarde
                
                meses_del_control = control.periodo.mes_control
                peso, talla, pc = get_realistic_growth(meses_del_control)
                
                control.pesokg = peso
                control.talla_cm = talla
                control.pc_cm = pc
                if control.talla_cm > 0:
                    control.imc = round(control.pesokg / ((control.talla_cm / 100) ** 2), 2)
                
                control.calificacion_nutricional = 'Normal'
                control.profesional = profesional_a_cargo
                controles_a_actualizar.append(control)

        for vacuna_app in vacunas_pasadas:
            if random.random() < 0.2: # 20% de chance de saltarse una vacuna
                pass # Se queda pendiente
            else:
                vacuna_app.fecha_aplicacion = vacuna_app.fecha_programada + timedelta(days=random.randint(0, 10))
                vacuna_app.profesional = profesional_a_cargo
                vacunas_a_actualizar.append(vacuna_app)

    # --- PERFIL: CASO DE RIESGO / BAJA ADHERENCIA (10%) ---
    else:
        # Este niño tiene grandes lagunas o datos atípicos
        for control in controles_pasados:
            if random.random() < 0.5: # 50% de chance de saltarse cada control
                pass # Se queda pendiente
            else:
                control.estado_control = 'Realizado'
                control.fecha_realizacion_control = control.fecha_control_programada + timedelta(days=random.randint(10, 40)) # Muy tarde
                
                meses_del_control = control.periodo.mes_control
                peso, talla, pc = get_realistic_growth(meses_del_control)
                
                # --- LÓGICA DE EJEMPLO PARA BI ---
                # Si el niño es del "Sector Azul" y es invierno, su peso será menor
                es_invierno = control.fecha_control_programada.month in [6, 7, 8]
                if nino.sector == 'Sector Azul' and es_invierno:
                    peso *= 0.90 # Reducimos el peso simulado en un 10%
                    control.calificacion_nutricional = 'Riesgo Desnutrición'
                else:
                    control.calificacion_nutricional = 'Normal'
                # --- FIN LÓGICA BI ---
                
                control.pesokg = round(peso, 1)
                control.talla_cm = round(talla, 1)
                control.pc_cm = round(pc, 1)
                if control.talla_cm > 0:
                    control.imc = round(control.pesokg / ((control.talla_cm / 100) ** 2), 2)
                
                control.profesional = profesional_a_cargo
                controles_a_actualizar.append(control)

        # Vacunas también tienen baja adherencia
        for vacuna_app in vacunas_pasadas:
            if random.random() < 0.4: # 40% de chance de saltarse cada vacuna
                pass
            else:
                vacuna_app.fecha_aplicacion = vacuna_app.fecha_programada + timedelta(days=random.randint(0, 10))
                vacuna_app.profesional = profesional_a_cargo
                vacunas_a_actualizar.append(vacuna_app)

    # --- 1.D. Simular Alergias (para un 20% de los niños) ---
    if categorias_alergia and random.random() < 0.20:
        agentes_comunes = {
            'Alimentaria': ['Maní', 'Lactosa', 'Huevo', 'Trigo'],
            'Fármacos': ['Penicilina', 'Ibuprofeno'],
            'Respiratoria': ['Polvo', 'Polen', 'Ácaros'],
        }
        categoria_obj = random.choice(categorias_alergia)
        agente = random.choice(agentes_comunes.get(categoria_obj.nombre, ['Desconocido']))
        fecha_diag = nino.fecha_nacimiento + timedelta(days=random.randint(30, 700))
        
        alergias_a_crear.append(
            RegistroAlergias(
                nino=nino, categoria=categoria_obj, agente_especifico=agente,
                mecanismo_inmunitario=random.choice(['TIPO_I', 'TIPO_IV', 'NO_ESPECIFICADO']),
                fecha_aparicion=fecha_diag, observaciones=fake.sentence(nb_words=8)
            )
        )

# --- 2. Guardamos todos los cambios en la BD (Operaciones en Bloque) ---
if ninos_a_actualizar_estado:
    Nino.objects.bulk_update(ninos_a_actualizar_estado, ['estado_seguimiento'])
    print(f"\n-> {len(ninos_a_actualizar_estado)} niños actualizados a 'Programa Completado'.")

if controles_a_actualizar:
    campos_control = [
        'estado_control', 'fecha_realizacion_control', 'pesokg', 'talla_cm', 'pc_cm', 'imc',
        'calificacion_nutricional', 'calificacion_estatural', 'profesional', 'deshabilitado'
    ]
    Control.objects.bulk_update(controles_a_actualizar, [f for f in campos_control if hasattr(Control, f)])
    print(f"-> {len(controles_a_actualizar)} controles pasados fueron actualizados.")

if vacunas_a_actualizar:
    campos_vacuna = ['fecha_aplicacion', 'dosis', 'lugar', 'profesional', 'deshabilitado']
    VacunaAplicada.objects.bulk_update(vacunas_a_actualizar, [f for f in campos_vacuna if hasattr(VacunaAplicada, f)])
    print(f"-> {len(vacunas_a_actualizar)} vacunas pasadas fueron actualizadas.")

if alergias_a_crear:
    RegistroAlergias.objects.bulk_create(alergias_a_crear, ignore_conflicts=True)
    print(f"-> {len(alergias_a_crear)} registros de alergias creados.")

print("\n¡Simulación de historiales por PERFIL completada!")