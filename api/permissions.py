from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre seulement aux propriétaires d'un objet de le modifier.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissions d'écriture seulement pour le propriétaire de l'objet
        return obj.owner == request.user

class IsPartnerOrAdmin(permissions.BasePermission):
    """
    Permission pour les partenaires et administrateurs
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_staff or request.user.is_partner
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Les partenaires peuvent seulement voir/modifier leurs propres données
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'partner'):
            return obj.partner.user == request.user
        
        return False