from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Check cookies for access_token
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None
        return self.get_user_and_token(raw_token)

    def get_user_and_token(self, raw_token):
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        return (user, validated_token)
