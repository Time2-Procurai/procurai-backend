from rest_framework.permissions import BasePermission
from apps.community.models import Community

class IsCommunityFollower(BasePermission):
    """
    Permissão que garante que o usuário só pode ver conteúdos da comunidade
    se ele for um seguidor dela.
    """
    message = "Você precisa seguir esta comunidade para acessar este conteúdo."

    def has_permission(self, request, view):
        community_id = view.kwargs.get('community_id')

        if not community_id:
            return False

        try:
            community = Community.objects.get(id=community_id)
        except Community.DoesNotExist:
            return False

        return community.seguidores.filter(id=request.user.id).exists()
