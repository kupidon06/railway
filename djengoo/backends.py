"""
Backend OAuth2 personnalisé pour Djengoo
Utilisé avec social-core pour l'authentification
"""

from social_core.backends.oauth import BaseOAuth2
from social_core.utils import handle_http_errors
import requests
from django.conf import settings

class DjengooOAuth2(BaseOAuth2):
    """
    Backend OAuth2 pour Djengoo IDP
    Adapté pour fonctionner avec votre IDP Django local
    """
    name = 'djengoo'
    
    # Configuration des endpoints pour votre IDP local
    AUTHORIZATION_URL = 'https://id.djengoo.com/o/authorize/'
    ACCESS_TOKEN_URL = 'https://id.djengoo.com/o/token/'
    USERINFO_URL = 'https://id.djengoo.com/o/userinfo/'
    ACCESS_TOKEN_METHOD = 'POST'
    DEFAULT_SCOPE = getattr(settings, 'SOCIAL_AUTH_DJENGO_SCOPE', ['openid', 'profile', 'email'])
    
    def get_key_and_secret(self):
        """
        Retourne le client ID et secret depuis les settings
        """
        client_id = getattr(settings, 'SOCIAL_AUTH_DJENGO_CLIENT_ID', '')
        client_secret = getattr(settings, 'SOCIAL_AUTH_DJENGO_CLIENT_SECRET', '')
        return client_id, client_secret
    
    def get_redirect_uri(self):
        """
        Retourne le redirect URI configuré
        """
        return getattr(settings, 'REDIRECT_URI', 'http://localhost:8000/callback/')
    
    def get_user_details(self, response):
        """
        Retourne les détails utilisateur depuis la réponse de l'IDP
        """
        username = response.get('preferred_username') or response.get('sub')
        fullname = response.get('name', '')
        first_name = response.get('given_name', '')
        last_name = response.get('family_name', '')
        
        if fullname and not (first_name or last_name):
            # Séparer le nom complet si nécessaire
            parts = fullname.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
        
        return {
            'username': username,
            'email': response.get('email'),
            'fullname': fullname,
            'first_name': first_name,
            'last_name': last_name,
        }
    
    def user_data(self, access_token, *args, **kwargs):
        """
        Récupère les données utilisateur depuis l'endpoint userinfo
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(
                self.USERINFO_URL,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Error retrieving user data: {e}")
    
    @handle_http_errors
    def auth_complete(self, *args, **kwargs):
        """
        Complète le processus d'authentification
        Gère l'échange du code contre un token d'accès
        """
        # Récupérer le code d'autorisation
        code = self.data.get('code')
        if not code:
            raise ValueError("No authorization code received")
        
        # Échanger le code contre un token
        token_data = self.get_access_token(code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise ValueError("No access token received")
        
        # Récupérer les données utilisateur
        user_data = self.user_data(access_token)
        
        # Créer et retourner la réponse d'authentification
        return self.strategy.authenticate(
            backend=self,
            response=user_data,
            access_token=access_token,
            refresh_token=token_data.get('refresh_token'),
            token_type=token_data.get('token_type', 'Bearer'),
            expires_in=token_data.get('expires_in')
        )
    
    def get_access_token(self, code, redirect_uri=None):
        """
        Échange le code d'autorisation contre un token d'accès
        """
        client_id, client_secret = self.get_key_and_secret()
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri or self.get_redirect_uri(),
            'client_id': client_id,
            'client_secret': client_secret,
        }
        
        # Ajouter PKCE si disponible
        if hasattr(self.strategy, '_pkce_code_verifier'):
            data['code_verifier'] = self.strategy._pkce_code_verifier
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.post(
                self.ACCESS_TOKEN_URL,
                data=data,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Error exchanging code for token: {e}")
    
    def auth_url(self):
        """
        Génère l'URL d'authentification avec PKCE
        """
        # Générer PKCE
        import base64
        import hashlib
        import secrets
        
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).rstrip(b'=').decode()
        
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b'=').decode()
        
        # Stocker pour l'échange du token
        self.strategy._pkce_code_verifier = code_verifier
        
        # Construire l'URL exactement comme votre code de test
        client_id, _ = self.get_key_and_secret()
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': self.get_redirect_uri(),  # Utilise la méthode
            'scope': ' '.join(getattr(settings, 'SOCIAL_AUTH_DJENGO_SCOPE', ['openid', 'profile', 'email'])),
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        from urllib.parse import urlencode
        return self.AUTHORIZATION_URL + '?' + urlencode(params)
