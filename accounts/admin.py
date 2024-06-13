from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Stylist, Customer, Seller, UserFollows, PortraitUpload, UserItemLikes
from django.utils.timezone import now

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ['username', 'id', 'email', 'is_superuser']

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_stylist', 'name', 'bio', 'pfp')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_stylist', 'name', 'bio', 'pfp')}),
    )
admin.site.register(CustomUser, CustomUserAdmin)



class StylistAdmin(admin.ModelAdmin):
    list_display = ['user', 'credits']
admin.site.register(Stylist, StylistAdmin)




class CustomerAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'height', 'weight']

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'username'
admin.site.register(Customer, CustomerAdmin)




class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_sold', 'total_sales', 'fumio_profit', 'seller_profit']
    search_fields = ['user__username']
    list_filter = ['items_sold', 'total_sales']
admin.site.register(Seller, SellerAdmin)



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