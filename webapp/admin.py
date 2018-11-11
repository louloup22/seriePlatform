from django.contrib import admin
from .models import Serie
from django.utils.text import Truncator
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class SerieAdmin(admin.ModelAdmin):
    list_display = ('name','nb_seasons','genres','short_overview','next_episode','next_episode_date')
    list_filter = ('name','genres',)
    date_hierarchy = 'last_episode_date'
    #ordering = ('-last_episode_date')
    searchfields = ('name','genres','overview')
    fields = ('name','nb_seasons','genres','short_overview','next_episode','next_episode_date')
    
    def short_overview(self, serie):
        return Truncator(serie.overview).chars(200, truncate='...')
    short_overview.short_description = 'Glimpse of overview'

admin.site.register(Serie,SerieAdmin)

#from .models import Profil
#
#class ProfileInline(admin.StackedInline):
#    model = Profil
#    can_delete = False
#    verbose_name_plural = 'Profil'
#    fk_name = 'user'
#
#class CustomUserAdmin(UserAdmin):
#    inlines = (ProfileInline, )
#
#    def get_inline_instances(self, request, obj=None):
#        if not obj:
#            return list()
#        return super(CustomUserAdmin, self).get_inline_instances(request, obj)
#
#
#admin.site.unregister(User)
#admin.site.register(User, CustomUserAdmin)