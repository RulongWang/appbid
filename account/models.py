__author__ = 'rulongwang'
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class UserPrivateItem(models.Model):
    """UserPrivateItem table info - such as is_bid_approved."""
    key = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)


class UserPrivateItemAdmin(admin.ModelAdmin):
    """The set of UserPrivateItem table displaying in admin page."""
    list_display = ('key', 'description')


class UserPrivateSetting(models.Model):
    """UserPrivateSetting table info."""
    user = models.ForeignKey(User)
    user_private_item = models.ForeignKey(UserPrivateItem)
    value = models.TextField()


class UserDetail(models.Model):
    """UserDetail table info."""
    user = models.OneToOneField(User)
    birthday = models.DateTimeField(blank=True, null=True)
    real_name = models.CharField(blank=True, max_length=255, null=True)
    street_address = models.CharField(blank=True, max_length=300, null=True)
    city = models.CharField(blank=True, max_length=255, null=True)
    state_provience = models.CharField(blank=True, max_length=255, null=True)
    post_code = models.CharField(blank=True, max_length=255, null=True)
    country = models.CharField(blank=True, max_length=255, null=True)


class UserDetailAdmin(admin.ModelAdmin):
    """The set of UserDetail table displaying in admin page."""
    list_display = ('user', 'real_name', 'city', 'country')


class UserPublicProfile(models.Model):
    """UserPublicProfile table info."""
    GENDER_TYPES = (
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Secret'),
    )
    user = models.OneToOneField(User)
    thumbnail = models.FilePathField(blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_TYPES, blank=True, default=3, null=True)
    homepage = models.CharField(max_length=255, blank=True, null=True)
    twitter_account = models.CharField(max_length=255, blank=True, null=True)
    facebook_account = models.CharField(max_length=255, blank=True, null=True)
    weibo_account = models.CharField(max_length=255, blank=True, null=True)
    weixin_account = models.CharField(max_length=255, blank=True, null=True)


class UserPublicProfileAdmin(admin.ModelAdmin):
    """The set of UserPublicProfile table displaying in admin page."""
    list_display = ('user', 'gender', 'homepage', 'weibo_account')


class Account(models.Model):
    """Account table info - support paypal, alipay now."""
    ACCOUNT_TYPE = (
        (1, 'paypal'),
        (2, 'alipay'),
    )
    user = models.ForeignKey(User)
    type = models.IntegerField(choices=ACCOUNT_TYPE)
    value = models.EmailField()


class AccountAdmin(admin.ModelAdmin):
    """The set of Account table displaying in admin page."""
    list_display = ('user', 'type', 'value')


class EmailItem(models.Model):
    """EmailSetting table info - email notification."""
    user = models.ManyToManyField(User)
    item = models.CharField(max_length=255)


class EmailItemAdmin(admin.ModelAdmin):
    """The set of EmailItem table displaying in admin page."""
    list_display = ('id', 'item')


admin.site.register(UserPrivateItem, UserPrivateItemAdmin)
admin.site.register(UserDetail, UserDetailAdmin)
admin.site.register(EmailItem, EmailItemAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(UserPublicProfile, UserPublicProfileAdmin)




