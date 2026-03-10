from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserSerializer
from .models import User
from bookings.models import Ticket
from notifications.models import Notification
from payments.models import Receipt


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
        age_raw = request.POST.get('age', '')

        if password != password2:
            return render(request, 'users/register.html', {'error': 'Пароли не совпадают!'})

        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Такой пользователь уже существует!'})

        age = int(age_raw) if age_raw.strip().isdigit() else None
        is_pensioner_pending = age is not None and age >= 60

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            age=age,
            is_pensioner_pending=is_pensioner_pending
        )

        if is_pensioner_pending:
            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                Notification.objects.create(
                    recipient=admin,
                    message=f'👴 Пользователь «{username}» (возраст {age} лет) запрашивает статус пенсионера. Подтвердите в панели управления во вкладке «Пенсионеры».'
                )

        login(request, user)
        return redirect('/')

    return render(request, 'users/register.html')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def account_view(request):
    tab = request.GET.get('tab', 'active')

    if request.GET.get('mark_all') == '1':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return redirect('/account/?tab=notifications')

    if tab == 'notifications':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)

    all_tickets = Ticket.objects.filter(booking__user=request.user).order_by('-created_at')
    active_tickets = [t for t in all_tickets if t.is_active()]
    used_tickets = [t for t in all_tickets if not t.is_active()]

    # Собираем скидки по booking_id
    receipts = Receipt.objects.filter(
        payment__booking__user=request.user,
        discount_amount__gt=0
    )
    discount_map = {}
    for r in receipts:
        discount_map[r.payment.booking_id] = {
            'discount_amount': r.discount_amount,
            'original_amount': r.original_amount,
            'final_amount': r.payment.amount,
        }

    active_paginator = Paginator(active_tickets, 7)
    active_page = request.GET.get('active_page', 1)
    active_tickets_page = active_paginator.get_page(active_page)

    used_paginator = Paginator(used_tickets, 7)
    used_page = request.GET.get('used_page', 1)
    used_tickets_page = used_paginator.get_page(used_page)

    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    pensioners_pending = User.objects.filter(is_pensioner_pending=True)

    return render(request, 'users/account.html', {
        'active_tickets': active_tickets_page,
        'used_tickets': used_tickets_page,
        'active_count': len(active_tickets),
        'used_count': len(used_tickets),
        'total_count': all_tickets.count(),
        'notifications': notifications,
        'unread_count': unread_count,
        'tab': tab,
        'pensioners_pending': pensioners_pending,
        'discount_map': discount_map,
    })


@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        if request.POST.get('avatar_only'):
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
                user.save()
        else:
            user.email = request.POST.get('email', user.email)
            user.phone = request.POST.get('phone', user.phone)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
            user.save()
            messages.success(request, 'Профиль успешно обновлён!')
        return redirect('/profile/')
    return render(request, 'users/profile.html')


@login_required
def apply_pensioner_view(request):
    if request.method == 'POST':
        user = request.user
        if not user.is_pensioner and not user.is_pensioner_pending:
            user.is_pensioner_pending = True
            user.save()
            messages.success(request, 'Заявка на статус пенсионера отправлена!')
            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                Notification.objects.create(
                    recipient=admin,
                    message=f'👴 Пользователь «{user.username}» (возраст {user.age} лет) запрашивает статус пенсионера. Подтвердите в панели управления во вкладке «Пенсионеры».'
                )
    return redirect('/profile/')


@login_required
def cancel_pensioner_view(request):
    if request.method == 'POST':
        user = request.user
        user.is_pensioner_pending = False
        user.save()
        messages.success(request, 'Заявка отозвана. Вы можете подать её снова.')
    return redirect('/profile/')