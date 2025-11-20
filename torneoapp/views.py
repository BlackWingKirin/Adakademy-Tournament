from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import random
import itertools
from .models import Equipo, Reto, Partido

def index(request):
    return render(request, 'index.html')

def sorteo(request):
    if request.method == 'POST':
        # Verificar si es para agregar equipo
        if 'agregar_equipo' in request.POST:
            nombre = request.POST.get('nombre')
            escuela = request.POST.get('escuela', '')
            if nombre:
                Equipo.objects.create(nombre=nombre, escuela=escuela)
                messages.success(request, f'Equipo {nombre} agregado correctamente.')
            return redirect('sorteo')
        
        # Verificar si es para eliminar todos los equipos
        elif 'eliminar_todos' in request.POST:
            count = Equipo.objects.count()
            Equipo.objects.all().delete()
            Partido.objects.all().delete()
            messages.success(request, f'{count} equipos eliminados correctamente.')
            return redirect('sorteo')
        
        # Verificar si es para realizar sorteo de fase de grupos
        elif 'realizar_sorteo' in request.POST:
            equipos = list(Equipo.objects.all())
            
            if len(equipos) != 5:
                messages.error(request, 'Se necesitan exactamente 5 equipos para el torneo.')
                return redirect('sorteo')
            
            # Limpiar partidos anteriores y puntos
            Partido.objects.all().delete()
            Equipo.objects.all().update(puntos=0)
            
            # Crear todos los enfrentamientos posibles (todos contra todos)
            partidos = []
            combinaciones = list(itertools.combinations(equipos, 2))
            
            for equipo1, equipo2 in combinaciones:
                partido = Partido.objects.create(
                    equipo1=equipo1,
                    equipo2=equipo2,
                    fase='GRUPOS'
                )
                partidos.append(partido)
            
            messages.success(request, 'Sorteo realizado! Se han creado todos los enfrentamientos de la fase de grupos.')
            return redirect('resultados_sorteo')
        
        # Verificar si es para generar semifinales
        elif 'generar_semifinales' in request.POST:
            # Obtener los 4 equipos con más puntos
            top_4 = Equipo.objects.order_by('-puntos')[:4]
            
            if len(top_4) != 4:
                messages.error(request, 'No hay suficientes equipos con puntos para generar semifinales.')
                return redirect('resultados_sorteo')
            
            # Crear partidos de semifinales
            Partido.objects.filter(fase='SEMIFINAL').delete()  # Limpiar semifinales anteriores
            
            partido1 = Partido.objects.create(
                equipo1=top_4[0],
                equipo2=top_4[3],
                fase='SEMIFINAL'
            )
            
            partido2 = Partido.objects.create(
                equipo1=top_4[1],
                equipo2=top_4[2],
                fase='SEMIFINAL'
            )
            
            messages.success(request, 'Semifinales generadas!')
            return redirect('resultados_sorteo')
        
        # Verificar si es para generar final
        elif 'generar_final' in request.POST:
            # Obtener ganadores de semifinales
            semifinales = Partido.objects.filter(fase='SEMIFINAL', ganador__isnull=False)
            
            if semifinales.count() != 2:
                messages.error(request, 'Ambas semifinales deben tener un ganador definido.')
                return redirect('resultados_sorteo')
            
            ganadores = [partido.ganador for partido in semifinales]
            
            # Crear partido final
            Partido.objects.filter(fase='FINAL').delete()  # Limpiar final anterior
            
            Partido.objects.create(
                equipo1=ganadores[0],
                equipo2=ganadores[1],
                fase='FINAL'
            )
            
            messages.success(request, 'Final generada!')
            return redirect('resultados_sorteo')
    
    # GET request - mostrar formulario
    equipos = Equipo.objects.all()
    context = {
        'equipos': equipos,
    }
    return render(request, 'sorteo.html', context)

def resultados_sorteo(request):
    """Vista para mostrar todos los resultados del torneo"""
    equipos = Equipo.objects.all().order_by('-puntos', 'nombre')
    partidos_grupos = Partido.objects.filter(fase='GRUPOS').order_by('creado_en')
    partidos_semifinales = Partido.objects.filter(fase='SEMIFINAL')
    partido_final = Partido.objects.filter(fase='FINAL').first()
    
    # Verificar si se pueden generar semifinales
    puede_generar_semifinales = (
        equipos.count() >= 4 and 
        Partido.objects.filter(fase='SEMIFINAL').count() == 0 and
        Partido.objects.filter(fase='GRUPOS', ganador__isnull=False).count() >= 6  # Al menos 6 partidos jugados
    )
    
    # Verificar si se puede generar final
    puede_generar_final = (
        Partido.objects.filter(fase='SEMIFINAL', ganador__isnull=False).count() == 2 and
        Partido.objects.filter(fase='FINAL').count() == 0
    )
    
    context = {
        'equipos': equipos,
        'partidos_grupos': partidos_grupos,
        'partidos_semifinales': partidos_semifinales,
        'partido_final': partido_final,
        'puede_generar_semifinales': puede_generar_semifinales,
        'puede_generar_final': puede_generar_final,
        'total_equipos': equipos.count(),
    }
    return render(request, 'resultados.html', context)

def registrar_resultado(request, partido_id):
    """Vista para registrar el resultado de un partido"""
    partido = get_object_or_404(Partido, id=partido_id)
    
    if request.method == 'POST':
        resultado1 = int(request.POST.get('resultado1', 0))
        resultado2 = int(request.POST.get('resultado2', 0))
        
        partido.resultado_equipo1 = resultado1
        partido.resultado_equipo2 = resultado2
        partido.estado = 'F'
        
        # Determinar ganador
        if resultado1 > resultado2:
            partido.ganador = partido.equipo1
            # Asignar puntos (3 por victoria)
            partido.equipo1.puntos += 3
            partido.equipo1.save()
        elif resultado2 > resultado1:
            partido.ganador = partido.equipo2
            partido.equipo2.puntos += 3
            partido.equipo2.save()
        else:
            # Empate - 1 punto para cada uno
            partido.equipo1.puntos += 1
            partido.equipo2.puntos += 1
            partido.equipo1.save()
            partido.equipo2.save()
        
        partido.save()
        messages.success(request, f'Resultado registrado: {partido.equipo1} {resultado1}-{resultado2} {partido.equipo2}')
        return redirect('resultados_sorteo')
    
    context = {
        'partido': partido,
    }
    return render(request, 'registrar_resultado.html', context)

def ruleta(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    
    if request.method == 'POST':
        # Asignar reto aleatorio
        retos = list(Reto.objects.all())
        reto_asignado = random.choice(retos)
        partido.reto = reto_asignado
        partido.save()
        
        messages.success(request, f'Reto "{reto_asignado.nombre}" asignado al partido.')
        return redirect('resultados_sorteo')
    
    context = {
        'partido': partido,
    }
    return render(request, 'ruleta.html', context)


def cargar_datos_iniciales(request):
    # Crear retos si no existen
    if not Reto.objects.exists():
        retos_data = [
            {
                'nombre': 'El Puente de Cristal',
                'descripcion': 'Versión robótica del juego clásico. Los mBots deben cruzar el tablero eligiendo la casilla correcta en cada paso.',
                'instrucciones': 'Programación por tiempos. No usar sensores. Ruta secreta: A1 -> B2 -> C2 -> D3 -> E4 -> F5'
            },
            {
                'nombre': 'Carrera de la Serpiente Obstaculizada',
                'descripcion': 'Carrera de velocidad con obstáculos fijos. El que termine primero gana, pero chocar con obstáculos conlleva penalización.',
                'instrucciones': 'Recorrido: A6 -> F6 -> F1 -> A1. Penalización: +5 segundos por obstáculo derribado.'
            },
            {
                'nombre': 'El Guardián del Tesoro',
                'descripcion': 'Juego de estrategia y precisión. Deben alcanzar un objeto en el centro del tablero evitando zonas de peligro.',
                'instrucciones': 'Tesoro en D3. Zonas de peligro: fila 2 y columna E. El Guardián elimina mBots en zonas de peligro.'
            }
        ]
        
        for reto_data in retos_data:
            Reto.objects.create(**reto_data)
    
    return JsonResponse({'success': True})