
from django.urls import path
from . import views
from .views import PasswordResetRequestView, PasswordResetConfirmView, PasswordResetRequestView1, PasswordResetConfirmView1, PasswordResetValidateCodeView
from .views import (
    ClienteProfileRegistrationView, 
    Tela1UserRegistrationView, 
    Tela2LojistaProfileView, 
    Tela3LojistaEnderecoView,
    DeletarContaView,
    UserProfileView,
    ChangePasswordView
)
from rest_framework_simplejwt.views import TokenRefreshView
from apps.user.views import MyTokenObtainPairView

app_name = 'user'

urlpatterns = [
    path('register/tela1/', Tela1UserRegistrationView.as_view(), name='register-tela1'),
    path('listar/usuarios/', views.UserListView.as_view(), name='user-list'),
    path('listar/usuarios/<int:user_id>/', views.GetUserByIdView.as_view(), name='user-detail'),
    path('register/tela2/lojista/<int:user_id>/', Tela2LojistaProfileView.as_view(), name='register-tela2'),
    path('register/tela3/lojista/<int:user_id>/', Tela3LojistaEnderecoView.as_view(),name='register-step3-lojista'),
    path('register/tela2/cliente/<int:user_id>/', ClienteProfileRegistrationView.as_view(), name='register-tela2-cliente'),     
    path('delete-account/', DeletarContaView.as_view(), name='deletar-conta'),
    path('listar/empresas/', views.EmpresaListView.as_view(), name='empresa-list'),
    path('listar/clientes/', views.ClienteListView.as_view(), name='cliente-list'),
    # Rotas de Login/Refresh
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rotas de Perfil
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    # Rota para PEDIR o e-mail (o que seu ForgotPasswordPage usa)
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    
    # Recuperação de senha

    path("password-reset/request/", PasswordResetRequestView1.as_view(), name="password-reset-request"),

    path('password-reset/validate/', PasswordResetValidateCodeView.as_view(), name='password-reset-validate'),

    path("password-reset/confirm/", PasswordResetConfirmView1.as_view(), name="password-reset-confirm"),
]

