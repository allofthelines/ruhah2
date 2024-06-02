from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Stylist, Customer, Seller, Supplier, UserFollows

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




class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'location', 'items_sold']
    search_fields = ['name', 'location']
    list_filter = ['items_sold', 'total_sales']
admin.site.register(Supplier, SupplierAdmin)




class UserFollowsAdmin(admin.ModelAdmin):
    list_display = ('user_from', 'user_to', 'created')
    search_fields = ('user_from__username', 'user_to__username')
    list_filter = ('created',)
    raw_id_fields = ('user_from', 'user_to')
admin.site.register(UserFollows, UserFollowsAdmin)