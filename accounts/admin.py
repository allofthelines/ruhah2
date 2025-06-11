from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Customer, UserFollows, PortraitUpload, UserItemLikes, UserItemCart, InviteCode, GridPicUpload
from django.utils.timezone import now
from datetime import datetime, timezone
from django.utils.html import mark_safe


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ['username', 'lifeform', 'id', 'email', 'is_superuser']
    list_filter = ('lifeform',)

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_stylist', 'name', 'lifeform', 'bio', 'pfp', 'profile_visibility', 'trending_mode', 'studio_visibility', 'accept_private_asks', 'private_ask_price', 'trending_styles', 'studio_styles', 'credits', 'new_email', 'email_change_requested_at')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_stylist', 'name', 'lifeform', 'bio', 'pfp', 'profile_visibility', 'trending_mode', 'studio_visibility', 'accept_private_asks', 'private_ask_price', 'trending_styles', 'studio_styles', 'credits', 'new_email', 'email_change_requested_at')}),
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
    list_display = ('id', 'thumbnail', 'liker_username', 'item', 'styler_username', 'liked_at', 'days_alive')
    list_filter = ('liker', 'styler')
    readonly_fields = ('id', 'liked_at')
    search_fields = ('liker__username', 'styler__username', 'item__itemid')

    def liker_username(self, obj):
        return obj.liker.username
    liker_username.admin_order_field = 'liker'  # Allows column order sorting
    liker_username.short_description = 'Liker'  # Renames column head

    def styler_username(self, obj):
        return obj.styler.username if obj.styler else 'None'
    styler_username.admin_order_field = 'styler'
    styler_username.short_description = 'Styler'

    def days_alive(self, obj):
        now = datetime.now(timezone.utc)
        delta = now - obj.liked_at
        return delta.days
    days_alive.short_description = 'Days Alive'

    def thumbnail(self, obj):
        if obj.item and obj.item.image:
            return mark_safe(f'<img src="{obj.item.image.url}" width="50" height="50" />')
        return 'No Image'
    thumbnail.short_description = 'Thumbnail'
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

class GridPicUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'tryon_state', 'gridpic_tryon_item_id',  'uploader_username', 'thumbnail', 'timedate_uploaded', 'deleted_by_uploader', 'age_in_days', )
    list_filter = ('deleted_by_uploader', 'timedate_uploaded')
    search_fields = ('uploader_id__username',)
    readonly_fields = ('timedate_uploaded',)

    def uploader_username(self, obj):
        return obj.uploader_id.username
    uploader_username.admin_order_field = 'uploader_id'
    uploader_username.short_description = 'Uploader'

    def thumbnail(self, obj):
        if obj.gridpic_processed_img:
            return mark_safe(f'<img src="{obj.gridpic_processed_img.url}" width="50" height="50" />')
        return 'No Image'
    thumbnail.short_description = 'Thumbnail'

    def age_in_days(self, obj):
        delta = now() - obj.timedate_uploaded
        return delta.days
    age_in_days.short_description = 'Age in Days'

admin.site.register(GridPicUpload, GridPicUploadAdmin)

class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('invite_code', 'is_used', 'created_at', 'inviter', 'invitee')
    search_fields = ('invite_code', 'inviter__username', 'invitee__username')
    list_filter = ('is_used', 'created_at')

admin.site.register(InviteCode, InviteCodeAdmin)