from django.urls import path
from . import views
from .views import ClienteProfileRegistrationView, Tela1UserRegistrationView, Tela2LojistaProfileView, Tela3LojistaEnderecoView,DeletarContaView
from rest_framework_simplejwt.views import TokenRefreshView
from apps.user.views import MyTokenObtainPairView

from .views import UserProfileView

from .views import Tela1UserRegistrationView, Tela2LojistaProfileView, Tela3LojistaEnderecoView

app_name = 'user'

urlpatterns = [
    path('register/tela1/', Tela1UserRegistrationView.as_view(), name='register-tela1'),
    path('listar/usuarios/', views.UserListView.as_view(), name='user-list'),
    path('register/tela2/lojista/<int:user_id>/', Tela2LojistaProfileView.as_view(), name='register-tela2'),
    path('register/tela3/lojista/<int:user_id>/', Tela3LojistaEnderecoView.as_view(),name='register-step3-lojista'),
    path('register/tela2/cliente/<int:user_id>/', ClienteProfileRegistrationView.as_view(), name='register-tela2-cliente'),    
    path('delete-account/', DeletarContaView.as_view(), name='deletar-conta'),
    # Rota para Login (Obter token)
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Rota para Refresh (Atualizar token)
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('api/products/', include('apps.products.urls')),

    path('register/tela3/lojista/<int:user_id>/', Tela3LojistaEnderecoView.as_view(),name='register-step3-lojista'),

    # Rota: GET ou PATCH para /api/user/profile/
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]


