from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sorteo/', views.sorteo, name='sorteo'),
    path('ruleta/<int:partido_id>/', views.ruleta, name='ruleta'),
    path('resultados/', views.resultados_sorteo, name='resultados_sorteo'),
    path('registrar-resultado/<int:partido_id>/', views.registrar_resultado, name='registrar_resultado'),
    path('cargar_datos/', views.cargar_datos_iniciales, name='cargar_datos'),
    path('reto/puente-cristal/', views.reto_puente_cristal, name='reto_puente_cristal'),
    path('reto/serpiente-obstaculizada/', views.reto_serpiente_obstaculizada, name='reto_serpiente_obstaculizada'),
    path('reto/guardian-tesoro/', views.reto_guardian_tesoro, name='reto_guardian_tesoro'),
]