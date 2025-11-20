from django.db import models

class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    escuela = models.CharField(max_length=100, blank=True)
    puntos = models.IntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

class Reto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    instrucciones = models.TextField()
    
    def __str__(self):
        return self.nombre

class Partido(models.Model):
    ESTADOS = [
        ('P', 'Programado'),
        ('E', 'En curso'),
        ('F', 'Finalizado'),
    ]
    
    FASE_CHOICES = [
        ('GRUPOS', 'Fase de Grupos'),
        ('SEMIFINAL', 'Semifinal'),
        ('FINAL', 'Final'),
    ]
    
    equipo1 = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_equipo1')
    equipo2 = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_equipo2')
    reto = models.ForeignKey(Reto, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    ganador = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=True, blank=True, related_name='partidos_ganados')
    fase = models.CharField(max_length=10, choices=FASE_CHOICES, default='GRUPOS')
    resultado_equipo1 = models.IntegerField(default=0)
    resultado_equipo2 = models.IntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.equipo1} vs {self.equipo2} - {self.fase}"