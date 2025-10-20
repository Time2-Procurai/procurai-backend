from django.urls import path
from . import views
from .views import ClienteProfileRegistrationView, Tela1UserRegistrationView, Tela2LojistaProfileView, Tela3LojistaEnderecoView,DeletarContaView

urlpatterns = [   
    path('register/tela1/', Tela1UserRegistrationView.as_view(), name='register-tela1'),

    path('register/tela2/lojista/<int:user_id>/', Tela2LojistaProfileView.as_view(), name='register-tela2'),

    path('register/tela3/lojista/<int:user_id>/', Tela3LojistaEnderecoView.as_view(),name='register-step3-lojista'),
    path('register/tela2/cliente/<int:user_id>/', ClienteProfileRegistrationView.as_view(), name='register-tela2-cliente'),
    path('register/tela3/lojista/<int:user_id>/', Tela3LojistaEnderecoView.as_view(), name='register-step3-lojista'),
    path('delete-account/', DeletarContaView.as_view(), name='deletar-conta'),
]
    
