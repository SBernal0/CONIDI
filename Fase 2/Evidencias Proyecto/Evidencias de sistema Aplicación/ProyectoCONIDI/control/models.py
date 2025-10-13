# control/models.py
from django.db import models
from datetime import date, timedelta # Asegúrate de tener este import
from simple_history.models import HistoricalRecords

# --- Modelos Geográficos ---
class Region(models.Model):
    id = models.AutoField(primary_key=True)
    nom_region = models.CharField(max_length=50)

    def __str__(self):
        return self.nom_region

class Ciudad(models.Model):
    id = models.AutoField(primary_key=True)
    nom_ciudad = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)

    def __str__(self):
        return self.nom_ciudad

class Comuna(models.Model):
    id = models.AutoField(primary_key=True)
    nom_comuna = models.CharField(max_length=50)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT)

    def __str__(self):
        return self.nom_comuna

# --- Modelo Principal del Niño ---
class Nino(models.Model):
    SEXO_CHOICES = [
        ('Masculino', 'Masculino'), 
        ('Femenino', 'Femenino')
    ]

    rut_nino = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=50)
    ap_paterno = models.CharField(max_length=30)
    ap_materno = models.CharField(max_length=30, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES)
    direccion = models.CharField(max_length=200)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nombre} {self.ap_paterno}"

# --- Modelos de Soporte para Controles ---
class PeriodoControl(models.Model):
    id = models.AutoField(primary_key=True)
    mes_control = models.IntegerField()
    nombre_mes_control = models.CharField(max_length=30)
    dias_margen = models.IntegerField(default=7)
    history = HistoricalRecords()

    def __str__(self):
        return self.nombre_mes_control

class Alergias(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_alergia = models.CharField(max_length=200)

    def __str__(self):
        return self.tipo_alergia

# --- Modelo Principal de Control ---
class Control(models.Model):
    TIPO_CONTROL_CHOICES = [
        ('Control_salud', 'Control de Salud'),
        ('Control_nutricional', 'Control Nutricional'),
        ('Control_preventivo', 'Control Preventivo'),
    ]
    INDI_ANTROPOMETRICOS_CHOICES = [
        ('PE', 'Peso/Edad'),
        ('PT', 'Peso/Talla'),
        ('TE', 'Talla/Edad'),
    ]
    CALIFICACION_ESTATURAL_CHOICES = [
        ('Talla Baja', 'Talla Baja'),
        ('Talla normal baja', 'Talla Normal Baja'),
        ('normal', 'Normal'),
        ('talla alta', 'Talla Alta'),
        ('talla normal alta', 'Talla Normal Alta'),
    ]
    CALIFICACION_PCE_CHOICES = [
        ('macrocefalia', 'Macrocefalia'),
        ('microcefalia', 'Microcefalia'),
        ('normal', 'Normal'),
    ]
    DIG_PA_CHOICES = [
        ('Hipertensión Etapa 2', 'Hipertensión Etapa 2'),
        ('Sospecha de Hipertensión Etapa 1', 'Sospecha de Hipertensión Etapa 1'),
        ('Sospecha de Prehipertensión', 'Sospecha de Prehipertensión'),
        ('normal', 'Normal'),
    ]

    id = models.AutoField(primary_key=True, db_column='contro_ninol_id')
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='controles')
    nombre_control = models.CharField(max_length=200)
    
    # --- CORREGIDO: Renombrado a 'fecha_control_programada' y cambiado a DateField ---
    periodo = models.ForeignKey(PeriodoControl, on_delete=models.PROTECT, null=True, blank=True)

    fecha_control_programada = models.DateField()
    fecha_realizacion_control = models.DateField(null=True, blank=True) # <-- CORREGIDO a DateField
    
    estado_control = models.CharField(max_length=30)
    # edad_meses = models.IntegerField() # <-- ELIMINADO: Campo redundante

    # Datos Antropométricos (ya estaban bien como opcionales)
    pesokg = models.FloatField(null=True, blank=True)
    talla_cm = models.FloatField(null=True, blank=True)
    imc = models.FloatField(null=True, blank=True)
    pc_cm = models.FloatField(verbose_name="Perímetro Craneal (cm)", null=True, blank=True)

    # Indicadores y Calificaciones (se recomienda hacerlos opcionales también)
    calificacion_nutricional = models.CharField(max_length=30, null=True, blank=True)
    calificacion_estatural = models.CharField(max_length=30, choices=CALIFICACION_ESTATURAL_CHOICES, null=True, blank=True)
    indi_antropometricos = models.CharField(max_length=10, choices=INDI_ANTROPOMETRICOS_CHOICES, null=True, blank=True)
    calificacion_pce = models.CharField(max_length=20, choices=CALIFICACION_PCE_CHOICES, null=True, blank=True)
    dig_pa = models.CharField(max_length=40, choices=DIG_PA_CHOICES, null=True, blank=True, verbose_name="Diagnóstico Presión Arterial")

    # Diagnóstico y Observaciones (CORREGIDO: Ahora son opcionales)
    diag_des_integral = models.TextField(verbose_name="Diagnóstico Desarrollo Integral", null=True, blank=True)
    obs_desarrollo_integral = models.TextField(verbose_name="Observaciones Desarrollo Integral", null=True, blank=True)
    indicaciones = models.TextField(null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Derivaciones (sin cambios)
    derivacion = models.BooleanField(default=False, db_column='derivación')
    consulta_dental_realizada = models.BooleanField(null=True, blank=True)
    derivacion_dentista = models.BooleanField(null=True, blank=True)

    # Profesional a cargo (CORREGIDO: Ahora es opcional)
    profesional = models.ForeignKey('login.Profesional', on_delete=models.PROTECT, null=True, blank=True)
    
    # Próximo control
    fecha_proximo_control = models.DateField(null=True, blank=True) # <-- CORREGIDO a DateField

    history = HistoricalRecords()

    @property
    def estado_alerta(self):
        # Si el control ya se realizó, no hay alerta.
        if self.fecha_realizacion_control:
            return "Realizado"

        hoy = date.today()
        fecha_programada = self.fecha_control_programada
        margen = self.periodo.dias_margen if self.periodo else 7

        # Lógica de alertas que definiste
        if hoy <= fecha_programada:
            return "Al día"
        elif hoy <= fecha_programada + timedelta(days=margen):
            return "Alerta Amarilla"
        else:
            return "Alerta Roja"

    @property
    def estado_css_class(self):
        estado = self.estado_alerta
        if estado == "Realizado":
            return "bg-success text-white"
        elif estado == "Al día":
            return "bg-primary text-white"
        elif estado == "Alerta Amarilla":
            return "bg-warning text-dark"
        elif estado == "Alerta Roja":
            return "bg-danger text-white"
        return "bg-secondary text-white"

    class Meta:
        verbose_name = "Control del Niño"
        verbose_name_plural = "Controles de Niños"

    def __str__(self):
        return f"Control {self.nombre_control} para {self.nino.nombre}"

# --- Otros Modelos del Historial Médico ---
class Vacuna(models.Model):
    id = models.AutoField(primary_key=True, db_column='vacuna_id')
    nom_vacuna = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return self.nom_vacuna

class VacunaAplicada(models.Model):
    VIA_CHOICES = [
        ('I.D', 'Intradérmica'), 
        ('I.M', 'Intramuscular'),
        ('S.C', 'Subcutánea'),
        ('V.O', 'Vía Oral'),
        ('N/A', 'No Aplica'),
    ]

    id = models.AutoField(primary_key=True, db_column='vacuna_aplicada_id')
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, db_column='rut_nino')
    vacuna = models.ForeignKey(Vacuna, on_delete=models.PROTECT)
    fecha_aplicacion = models.DateField()
    dosis = models.FloatField()
    lugar = models.CharField(max_length=100)
    negacion = models.BooleanField(default=False)
    via = models.CharField(max_length=10, choices=VIA_CHOICES, default='N/A')
    fecha_inoculacion = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.vacuna.nom_vacuna} para {self.nino.nombre}"

class RegistroAlergias(models.Model):
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, db_column='rut_nino')
    alergia = models.ForeignKey(Alergias, on_delete=models.PROTECT, db_column='id_alergia')
    fecha_aparicion = models.DateTimeField()
    fecha_remision = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('nino', 'alergia')

    def __str__(self):
        return f"Alergia {self.alergia.tipo_alergia} en {self.nino.nombre}"

class EntregaAlimentos(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_entrega')
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, db_column='rut_nino')
    fecha_entrega = models.DateField()
    fecha_entrega_efectiva = models.DateField(null=True, blank=True)
    entregado = models.BooleanField(default=False)

    def __str__(self):
        return f"Alimentos para {self.nino.nombre} en fecha {self.fecha_entrega}"