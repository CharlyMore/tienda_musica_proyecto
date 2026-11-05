from django.urls import path

from . import views

app_name = "instrumentos"

urlpatterns = [
    path("", views.iniciar_sesion, name="login"),
    path("tienda/", views.lista_instrumentos, name="lista"),
    path("cerrar-sesion/", views.cerrar_sesion, name="logout"),
    path("api/login/", views.LoginAPIView.as_view(), name="api_login"),
    path(
        "api/instrumentos/",
        views.InstrumentoListCreateAPIView.as_view(),
        name="api_instrumentos",
    ),
    path(
        "api/instrumentos/<int:pk>/",
        views.InstrumentoDetailAPIView.as_view(),
        name="api_instrumento_detalle",
    ),
    path("instrumentos/nuevo/", views.crear_instrumento, name="crear"),
    path("instrumentos/<int:pk>/", views.detalle_instrumento, name="detalle"),
    path("instrumentos/<int:pk>/editar/", views.editar_instrumento, name="editar"),
    path(
        "instrumentos/<int:pk>/eliminar/",
        views.eliminar_instrumento,
        name="eliminar",
    ),
]
