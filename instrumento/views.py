from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import InstrumentoForm
from .models import Instrumento


class InstrumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrumento
        fields = [
            "id",
            "nombre",
            "marca",
            "categoria",
            "precio",
            "stock",
            "descripcion",
        ]
        read_only_fields = ["id"]


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("instrumentos:lista")
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            error = "Ingresa tu usuario y contraseña."
        else:
            user = authenticate(
                request=request,
                username=username,
                password=password,
            )
            if user is None:
                error = "Usuario o contraseña incorrectos."
            else:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                request.session["api_token"] = token.key
                return redirect("instrumentos:lista")
    return render(request, "instrumentos/login.html", {"error": error})


def lista_instrumentos(request):
    respuesta = _redirigir_si_no_autenticado(request)
    if respuesta:
        return respuesta
    instrumentos = Instrumento.objects.all()
    return render(
        request,
        "instrumentos/lista.html",
        {
            "instrumentos": instrumentos,
            "total_instrumentos": instrumentos.count(),
            "total_categorias": len(Instrumento.Categoria.choices),
        },
    )


def detalle_instrumento(request, pk):
    respuesta = _redirigir_si_no_autenticado(request)
    if respuesta:
        return respuesta
    instrumento = get_object_or_404(Instrumento, pk=pk)
    return render(
        request,
        "instrumentos/detalle.html",
        {"instrumento": instrumento},
    )


def crear_instrumento(request):
    respuesta = _redirigir_si_no_autenticado(request)
    if respuesta:
        return respuesta
    form = InstrumentoForm(
        request.POST if request.method == "POST" else None
    )
    if request.method == "POST" and form.is_valid():
        instrumento = form.save()
        return redirect("instrumentos:detalle", pk=instrumento.pk)
    return render(
        request,
        "instrumentos/formulario.html",
        {"form": form, "titulo": "Agregar instrumento"},
    )


def editar_instrumento(request, pk):
    respuesta = _redirigir_si_no_autenticado(request)
    if respuesta:
        return respuesta
    instrumento = get_object_or_404(Instrumento, pk=pk)
    form = InstrumentoForm(
        request.POST if request.method == "POST" else None,
        instance=instrumento,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("instrumentos:detalle", pk=instrumento.pk)
    return render(
        request,
        "instrumentos/formulario.html",
        {"form": form, "titulo": "Editar instrumento", "instrumento": instrumento},
    )


def eliminar_instrumento(request, pk):
    respuesta = _redirigir_si_no_autenticado(request)
    if respuesta:
        return respuesta
    instrumento = get_object_or_404(Instrumento, pk=pk)
    if request.method == "POST":
        instrumento.delete()
        return redirect("instrumentos:lista")
    return render(
        request,
        "instrumentos/confirmar_eliminacion.html",
        {"instrumento": instrumento},
    )


def cerrar_sesion(request):
    respuesta = _redirigir_si_no_autenticado(request)
    if respuesta:
        return respuesta
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    Token.objects.filter(user=request.user).delete()
    logout(request)
    return redirect("instrumentos:login")


def _redirigir_si_no_autenticado(request):
    if not request.user.is_authenticated:
        return redirect_to_login(
            request.get_full_path(),
            "instrumentos:login",
        )
    return None


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if (
            not isinstance(username, str)
            or not username.strip()
            or not isinstance(password, str)
            or not password
        ):
            return Response(
                {"error": "Debes ingresar usuario y contraseña."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            request=request._request,
            username=username.strip(),
            password=password,
        )
        if user is None:
            return Response(
                {"error": "Usuario o contraseña incorrectos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "mensaje": "Autenticación correcta.",
                "usuario": user.get_username(),
                "token": token.key,
            },
            status=status.HTTP_200_OK,
        )


class InstrumentoListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, _request):
        instrumentos = Instrumento.objects.all()
        serializer = InstrumentoSerializer(instrumentos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = InstrumentoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instrumento = serializer.save()
        return Response(
            InstrumentoSerializer(instrumento).data,
            status=status.HTTP_201_CREATED,
        )


class InstrumentoDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_instrumento(self, pk):
        try:
            return Instrumento.objects.get(pk=pk)
        except Instrumento.DoesNotExist:
            return None

    def get(self, _request, pk):
        instrumento = self.get_instrumento(pk)
        if instrumento is None:
            return Response(
                {"error": "Instrumento no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            InstrumentoSerializer(instrumento).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        instrumento = self.get_instrumento(pk)
        if instrumento is None:
            return Response(
                {"error": "Instrumento no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = InstrumentoSerializer(instrumento, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, _request, pk):
        instrumento = self.get_instrumento(pk)
        if instrumento is None:
            return Response(
                {"error": "Instrumento no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        instrumento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
