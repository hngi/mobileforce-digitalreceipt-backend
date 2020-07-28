from django.contrib import admin

# Register your models here.

from .models import SecurityQuestion, UserToken, UserDetails, Token

admin.site.register(SecurityQuestion)
admin.site.register(UserToken)
admin.site.register(UserDetails)
admin.site.register(Token)