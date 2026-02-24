"""
Views pour l'authentification Djengoo dans le client Django
"""

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json


def home(request):
    """Page d'accueil"""
    if request.user.is_authenticated:
        return render(request, 'djengoo/home.html', {'user': request.user})
    return redirect('djengoo:login')


def djengoo_login(request):
    """
    Vue de connexion via Djengoo OAuth2
    """
    if request.user.is_authenticated:
        return redirect('/')

    # Nettoyer seulement le code verifier précédent (ne pas flush toute la session)
    request.session.pop('_pkce_code_verifier', None)
    
    # Générer PKCE et construire l'URL directement
    import base64
    import hashlib
    import secrets
    from urllib.parse import urlencode
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode()
    
    # Stocker le verifier pour le callback
    if not request.session.session_key:
        request.session.create()
    request.session['_pkce_code_verifier'] = code_verifier
    request.session.modified = True
    request.session.save()
    
    print(f"Login - Session key: {request.session.session_key}")
    print(f"Login - Session data: {dict(request.session)}")
    print(f"Login - Code verifier stored: {code_verifier[:10]}...")
    
    params = {
        'response_type': 'code',
        'client_id': getattr(settings, 'SOCIAL_AUTH_DJENGO_CLIENT_ID', ''),
        'redirect_uri': getattr(settings, 'REDIRECT_URI', 'http://localhost:8000/callback/'),
        'scope': 'openid profile email',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }

    # Silent login : ajouter prompt=none pour vérifier la session IDP sans UI
    if request.GET.get('silent', '').lower() == 'true':
        params['prompt'] = 'none'
        request.session['_silent_login'] = True
        request.session.save()

    auth_url = 'https://id.djengoo.com/o/authorize/?' + urlencode(params)
    return redirect(auth_url)





@require_http_methods(["POST"])
@csrf_exempt
def token_info(request):
    """
    Endpoint pour vérifier les informations d'un token
    Utile pour les applications SPA/React
    """
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')
        
        if not access_token:
            return JsonResponse({'error': 'Missing access_token'}, status=400)
        
        # Vérifier le token auprès de l'IDP
        response = requests.get(
            'https://id.djengoo.com/o/userinfo/',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            user_info = response.json()
            return JsonResponse({
                'valid': True,
                'user_info': user_info
            })
        else:
            return JsonResponse({
                'valid': False,
                'error': 'Invalid token'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'error': str(e)
        }, status=500)


@login_required
def logout_view(request):
    """
    Vue de déconnexion
    """
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect(settings.LOGIN_URL)


def callback(request):
    """
    Callback OAuth2 pour Djengoo - utilisant le backend personnalisé
    """
    from django.conf import settings
    from .backends import DjengooOAuth2
    
    error = request.GET.get("error")
    if error:
        # Silent login : si l'IDP retourne login_required, pas de session active
        # On redirige simplement vers la page d'accueil (qui affichera le login normal)
        if error == "login_required" and request.session.get('_silent_login'):
            request.session.pop('_silent_login', None)
            request.session.pop('_pkce_code_verifier', None)
            request.session.save()
            return redirect('/')

        error_description = request.GET.get("error_description", "")
        return HttpResponse(f"Erreur Djengoo : {error} - {error_description}", status=400)
    
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Code d'autorisation manquant", status=400)
    
    # Récupérer le code verifier depuis la session
    code_verifier = request.session.get('_pkce_code_verifier')
    print(f"Session key: {request.session.session_key}")
    print(f"Session data: {dict(request.session)}")
    print(f"Code verifier: {code_verifier}")
    
    if not code_verifier:
        return HttpResponse("Code verifier manquant en session", status=400)
    
    try:
        # Créer une stratégie complète pour le backend
        from social_core.strategy import BaseStrategy
        
        class CompleteDjangoStrategy(BaseStrategy):
            def __init__(self, request):
                self.request = request
                self._pkce_code_verifier = None
            
            def setting(self, name, default=None):
                from django.conf import settings
                return getattr(settings, name, default)
            
            def request_data(self, merge=True):
                if merge:
                    data = {}
                    data.update(self.request.GET.dict())
                    data.update(self.request.POST.dict())
                    return data
                return self.request.GET.dict()
            
            def request_host(self):
                return self.request.get_host()
            
            def redirect(self, url):
                from django.shortcuts import redirect
                return redirect(url)
            
            def session_set(self, name, value):
                self.request.session[name] = value
                self.request.session.modified = True
            
            def session_get(self, name, default=None):
                return self.request.session.get(name, default)
            
            def session_pop(self, name):
                return self.request.session.pop(name, None)
            
            def build_absolute_uri(self, path=None):
                from django.contrib.sites.shortcuts import get_current_site
                from django.conf import settings
                if path is None:
                    path = self.request.get_full_path()
                site = get_current_site(self.request)
                return f"{self.request.scheme}://{site.domain}{path}"
            
            def get_pipeline(self):
                return []
            
            def to_session(self, value, name):
                self.session_set(name, value)
            
            def from_session(self, name):
                return self.session_get(name)
            
            def clean_partial_pipeline(self, name):
                self.session_pop(name)
        
        # Créer une instance du backend avec la stratégie
        strategy = CompleteDjangoStrategy(request)
        backend = DjengooOAuth2(strategy=strategy)
        
        # Stocker le code verifier dans la stratégie pour PKCE
        backend.strategy._pkce_code_verifier = code_verifier
        
        # Utiliser le redirect URI dynamique comme dans le code qui fonctionne
        redirect_uri = request.build_absolute_uri('/callback/')
        
        # Échanger le code contre un token via le backend
        token_data = backend.get_access_token(code, redirect_uri=redirect_uri)
        access_token = token_data.get('access_token')
        
        if not access_token:
            return HttpResponse("Token d'accès non reçu", status=400)
        
        # Récupérer les données utilisateur via le backend
        user_data = backend.user_data(access_token)
        
        # Utiliser le backend pour créer/mettre à jour l'utilisateur
        user_details = backend.get_user_details(user_data)
        
        # Créer ou récupérer l'utilisateur
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user, created = User.objects.get_or_create(
            username=user_details['username'],
            defaults={
                'email': user_details['email'],
                'first_name': user_details['first_name'],
                'last_name': user_details['last_name'],
            }
        )
        
        # Mettre à jour si l'utilisateur existe déjà
        if not created:
            user.email = user_details['email']
            user.first_name = user_details['first_name']
            user.last_name = user_details['last_name']
            user.save()
        
        # Authentifier l'utilisateur avec le backend standard Django
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Nettoyer la session
        if '_pkce_code_verifier' in request.session:
            del request.session['_pkce_code_verifier']
        
        # Rediriger vers la page d'accueil
        return redirect('/')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Erreur lors du traitement du callback: {str(e)}", status=500)
