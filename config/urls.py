from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from movies.views import ( add_hall_view)

from movies.views import movie_list_view, movie_detail_view, add_review_view
from bookings.views import seat_selection_view, create_booking_view
from payments.views import payment_view, receipt_view, ticket_pdf_view
from users.views import login_view, register_view, logout_view, account_view
from movies.views import (
    movie_list_view, movie_detail_view, add_review_view,
    admin_panel_view, add_movie_view, delete_movie_view,
    add_actor_view, delete_actor_view,
    add_session_view, delete_session_view
)


@api_view(['GET'])
def api_root(request):
    return Response({
        '🔐 Авторизация': {
            'register': request.build_absolute_uri('/api/users/register/'),
            'login': request.build_absolute_uri('/api/users/login/'),
            'token_refresh': request.build_absolute_uri('/api/users/token/refresh/'),
            'profile': request.build_absolute_uri('/api/users/profile/'),
        },
        '🎬 Фильмы': {
            'list': request.build_absolute_uri('/api/movies/'),
            'detail': request.build_absolute_uri('/api/movies/<id>/'),
            'manage': request.build_absolute_uri('/api/movies/manage/'),
            'reviews': request.build_absolute_uri('/api/movies/<id>/reviews/'),
        },
        '🎭 Актёры': {
            'list': request.build_absolute_uri('/api/actors/'),
            'detail': request.build_absolute_uri('/api/actors/<id>/'),
        },
        '🎞️ Жанры': {
            'list': request.build_absolute_uri('/api/genres/'),
        },
        '🏛️ Залы': {
            'list': request.build_absolute_uri('/api/halls/'),
            'detail': request.build_absolute_uri('/api/halls/<id>/'),
        },
        '💺 Места': {
            'list': request.build_absolute_uri('/api/seats/'),
            'detail': request.build_absolute_uri('/api/seats/<id>/'),
        },
        '📅 Сеансы': {
            'list': request.build_absolute_uri('/api/sessions/'),
            'detail': request.build_absolute_uri('/api/sessions/<id>/'),
        },
        '🎟️ Бронирование': {
            'create': request.build_absolute_uri('/api/bookings/'),
            'cancel': request.build_absolute_uri('/api/bookings/<id>/cancel/'),
        },
        '🎫 Билеты': {
            'my_tickets': request.build_absolute_uri('/api/tickets/'),
            'detail': request.build_absolute_uri('/api/tickets/<id>/'),
        },
        '💳 Оплата': {
            'pay': request.build_absolute_uri('/api/pay/'),
            'my_receipts': request.build_absolute_uri('/api/receipts/'),
        },
        '🔔 Уведомления': {
            'list': request.build_absolute_uri('/api/notifications/'),
            'read_all': request.build_absolute_uri('/api/notifications/read-all/'),
        },
        '📖 Документация': {
            'swagger': request.build_absolute_uri('/api/docs/'),
        },
    })


urlpatterns = [
    path('admin/', admin.site.urls),

    # HTML страницы
    path('', movie_list_view, name='home'),
    path('movies/', movie_list_view, name='movie-list'),
    path('movies/<int:pk>/', movie_detail_view, name='movie-detail'),
    path('movies/<int:pk>/review/', add_review_view, name='add-review'),
    path('sessions/<int:pk>/seats/', seat_selection_view, name='seat-selection'),
    path('bookings/create/', create_booking_view, name='create-booking'),
    path('payment/<int:pk>/', payment_view, name='payment'),
    path('receipt/<str:receipt_number>/', receipt_view, name='receipt'),
    path('tickets/<int:pk>/pdf/', ticket_pdf_view, name='ticket-pdf'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('account/', account_view, name='account'),
# Админ панель HTML
path('admin-panel/', admin_panel_view, name='admin-panel'),
path('admin-panel/movie/add/', add_movie_view, name='add-movie'),
path('admin-panel/movie/<int:pk>/delete/', delete_movie_view, name='delete-movie'),
path('admin-panel/actor/add/', add_actor_view, name='add-actor'),
path('admin-panel/actor/<int:pk>/delete/', delete_actor_view, name='delete-actor'),
path('admin-panel/session/add/', add_session_view, name='add-session'),
path('admin-panel/session/<int:pk>/delete/', delete_session_view, name='delete-session'),
path('admin-panel/hall/add/', add_hall_view, name='add-hall'),
    # API
    path('api/', api_root, name='api-root'),
    path('api/users/', include('users.urls')),
    path('api/', include('movies.urls')),
    path('api/', include('bookings.urls')),
    path('api/', include('payments.urls')),
    path('api/', include('notifications.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)