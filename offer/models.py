__author__ = 'jia.qianpeng'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


def content_file_name(instance, filename):
    """The path of saving company icon. The pattern is publisher_id/filename"""
    return '/'.join([str(instance.publisher.id), filename])


# class Company(models.Model):
#     """Company table info."""
#     name = models.CharField(max_length=255, blank=True)
#     icon = models.FileField(max_length=255, upload_to=content_file_name)
#     url = models.URLField(max_length=255, null=True, blank=True)
#     description = models.TextField(null=True, blank=True)
#     create_time = models.DateTimeField(auto_now_add=True)


class Position(models.Model):
    """Position table info."""
    key = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name


class Offer(models.Model):
    """Offer table info."""
    OFFER_TYPES = (
        (1, 'FullTime'),
        (2, 'PartTime'),
    )
    CATEGORY = (
        (1, 'offer'),
        (2, 'project'),
    )
    SALARY_TYPES = (
        (1, 'Monthly Salary'),
        (2, 'Annual Salary'),
    )
    publisher = models.ForeignKey(User)
    # company = models.ForeignKey(Company, null=True, blank=True)
    status = models.BooleanField(default=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    category = models.IntegerField(choices=CATEGORY, null=True, blank=True, default=1)
    type = models.IntegerField(choices=OFFER_TYPES, null=True, blank=True, default=1)
    location = models.CharField(max_length=255, null=True, blank=True)
    position = models.ManyToManyField(Position, null=True, blank=True)
    begin_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    non_chinese_applicants = models.BooleanField(default=True)
    salary = models.CharField(max_length=255, blank=True)
    salary_type = models.IntegerField(choices=SALARY_TYPES, null=True, blank=True, default=1)
    description = models.TextField(null=True, blank=True)
    company_icon = models.FileField(max_length=255, upload_to=content_file_name, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_modify = models.DateTimeField(auto_now=True)


class OfferRecord(models.Model):
    """Offer record table info."""
    offer = models.OneToOneField(Offer)
    view_count = models.IntegerField(null=True, default=0, blank=True)
    apply_count = models.IntegerField(null=True, default=0, blank=True)


# class OfferApplicants(models.Model):
#     """Offer applicants table info."""
#     offer = models.ForeignKey(Offer)
#     applicant = models.ForeignKey(User)
#     apply_time = models.DateTimeField(auto_now_add=True)


#Need to init or edit the data by admin.
admin.site.register(Offer)
admin.site.register(Position)
admin.site.register(OfferRecord)