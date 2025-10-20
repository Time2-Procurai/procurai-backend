from django.urls import path
<<<<<<< HEAD
from . import views
from .views import ClienteProfileRegistrationView, Tela1UserRegistrationView, Tela2LojistaProfileView, Tela3LojistaEnderecoView,DeletarContaView

urlpatterns = [   
=======
from .views import Tela1UserRegistrationView, Tela2LojistaProfileView, Tela3LojistaEnderecoView

app_name = 'user'

urlpatterns = [
>>>>>>> dcf8ff9e5f7260a29d806f5a65faa73cf2608609
    path('register/tela1/', Tela1UserRegistrationView.as_view(), name='register-tela1'),

    path('register/tela2/lojista/<int:user_id>/', Tela2LojistaProfileView.as_view(), name='register-tela2'),

<<<<<<< HEAD
    path('register/tela3/lojista/<int:user_id>/', Tela3LojistaEnderecoView.as_view(),name='register-step3-lojista'),
    path('register/tela2/cliente/<int:user_id>/', ClienteProfileRegistrationView.as_view(), name='register-tela2-cliente'),
    path('register/tela3/lojista/<int:user_id>/', Tela3LojistaEnderecoView.as_view(), name='register-step3-lojista'),
    path('delete-account/', DeletarContaView.as_view(), name='deletar-conta'),
]
    
=======
    path('register/tela3/lojista/<int:user_id>/', Tela3LojistaEnderecoView.as_view(),name='register-step3-lojista'
    ),
]

>>>>>>> dcf8ff9e5f7260a29d806f5a65faa73cf2608609
