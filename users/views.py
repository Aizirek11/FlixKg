from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserSerializer
from .models import User
from bookings.models import Ticket


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')
        return render(request, 'users/login.html', {'error': 'Неверный логин или пароль!'})
    return render(request, 'users/login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            return render(request, 'users/register.html', {'error': 'Пароли не совпадают!'})

        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Такой пользователь уже существует!'})

        user = User.objects.create_user(username=username, email=email, password=password, phone=phone)
        login(request, user)
        return redirect('/')

    return render(request, 'users/register.html')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def account_view(request):
    tickets = Ticket.objects.filter(booking__user=request.user).order_by('-created_at')
    active_count = sum(1 for t in tickets if t.is_active())
    return render(request, 'users/account.html', {
        'tickets': tickets,
        'active_count': active_count,
    })