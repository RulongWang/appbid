__author__ = 'rulongwang'
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class UserProfile(models.Model):
    """UserProfile table info."""
    user = models.OneToOneField(User)
    is_bid_approved = models.BooleanField(default=False)


class UserDetails(models.Model):

    user = models.OneToOneField(User)
    birthday = models.DateTimeField(blank=True)
    real_name = models.CharField(blank=True,max_length=100)
    street_address = models.CharField(blank=True,max_length=300)
    city = models.CharField(blank=True,max_length=100)
    state_provience = models.CharField(blank=True, max_length=100)
    post_code = models.CharField(blank=True, max_length=10)
    country = models.CharField(blank=True,max_length=100)
    email = models.EmailField(blank=True)

    def __unicode__(self):
        return ' '.join(self.user).join(' detail')

class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user','real_name','city','country','email')

class UserPublicProfile(models.Model):
    GENDER_TYPES = (
        (1,'Male'),
        (2,'Female'),
        (3,'Secret'),
    )
    user = models.OneToOneField(User)
    thumbnail = models.FilePathField(blank=True)
    gender = models.BooleanField(GENDER_TYPES, blank=True,default=3)
    homepage = models.CharField(max_length=200,blank=True)
    twitter_account = models.CharField(max_length=30,blank=True,null=True)
    facebook_account = models.CharField(max_length=30,blank=True,null=True)
    weibo_account = models.CharField(max_length=30,blank=True,null=True)
    weixin_account = models.CharField(max_length=30, blank=True,null=True)
    def __unicode__(self):
        return ' '.join(self.user).join(' detail')


class UserPublicProfileAdmin(admin.ModelAdmin):
    list_display = ('user','gender','homepage','weibo_account')

class account(models.Model):
    #account,paypal or alipay
    account_type = (
        (1,'paypal'),
        (2,'alipay'),
    )
    user = models.OneToOneField(User)
    type = models.IntegerField(account_type)
    value = models.EmailField()
    def __unicode__(self):
        return ' '.join(self.user).join(self.type)

class accountAdmin(admin.ModelAdmin):
    list_display = ('user','type','value')

class email_items(models.Model):
    # email notification
    item = models.CharField(max_length=200)

    def __unicode__(self):
        return self.item

class email_items_Admin(admin.ModelAdmin):
    list_display = ('id','item')


class email_setting(models.Model):
    user = models.ForeignKey(User)
    setting_item = models.ForeignKey(email_items)
    value = models.BooleanField()

    def __unicode__(self):
        return ''.join(self.user).join(self.setting_item)

class email_setting_admin(admin.ModelAdmin):
    list_display = ('user','setting_item','value')


admin.site.register(UserProfile)
admin.site.register(UserDetails)
admin.site.register(email_items,email_items_Admin)
admin.site.register(email_setting,email_setting_admin)
admin.site.register(account,accountAdmin)
admin.site.register(UserPublicProfile,UserPublicProfileAdmin)




