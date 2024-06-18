from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Customer, UserFollows, PortraitUpload, UserItemLikes, UserItemCart
from django.utils.timezone import now

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ['username', 'id', 'email', 'is_superuser']

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_stylist', 'name', 'bio', 'pfp', 'profile_visibility', 'trending_mode', 'trending_styles', 'studio_styles', 'credits')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_stylist', 'name', 'bio', 'pfp', 'profile_visibility', 'trending_mode', 'trending_styles', 'studio_styles', 'credits')}),
    )
admin.site.register(CustomUser, CustomUserAdmin)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'height', 'weight']

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'username'
admin.site.register(Customer, CustomerAdmin)



class UserFollowsAdmin(admin.ModelAdmin):
    list_display = ('user_from', 'user_to', 'created')
    search_fields = ('user_from__username', 'user_to__username')
    list_filter = ('created',)
    raw_id_fields = ('user_from', 'user_to')
admin.site.register(UserFollows, UserFollowsAdmin)

class UserItemLikesAdmin(admin.ModelAdmin):
    list_display = ('id', 'liker_username', 'item', 'styler_username')
    list_filter = ('liker', 'styler')

    def liker_username(self, obj):
        return obj.liker.username
    liker_username.admin_order_field = 'liker'  # Allows column order sorting
    liker_username.short_description = 'Liker'  # Renames column head

    def styler_username(self, obj):
        return obj.styler.username if obj.styler else 'None'
    styler_username.admin_order_field = 'styler'
    styler_username.short_description = 'Styler'

admin.site.register(UserItemLikes, UserItemLikesAdmin)


class UserItemCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_username', 'item', 'styler_username')
    list_filter = ('buyer', 'styler')

    def buyer_username(self, obj):
        return obj.buyer.username if obj.buyer else 'None'
    buyer_username.admin_order_field = 'buyer'  # Allows column order sorting
    buyer_username.short_description = 'Buyer'  # Renames column head

    def styler_username(self, obj):
        return obj.styler.username if obj.styler else 'None'
    styler_username.admin_order_field = 'styler'
    styler_username.short_description = 'Styler'

admin.site.register(UserItemCart, UserItemCartAdmin)



class PortraitUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_id_int', 'wearer_id', 'portrait_img', 'status', 'age_in_hours')
    search_fields = ('ticket_id_int', 'wearer_id__username', 'status')
    list_filter = ('status',)
    readonly_fields = ('timedate_created',)

    def age_in_hours(self, obj):
        delta = now() - obj.timedate_created
        return int(delta.total_seconds() // 3600)

    age_in_hours.short_description = 'Age in Hours'  # Set a readable column name


admin.site.register(PortraitUpload, PortraitUploadAdmin)