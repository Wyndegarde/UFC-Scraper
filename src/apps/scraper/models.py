from django.db import models
from django.db.models import CharField, BooleanField, IntegerField, FloatField
from typing import Optional

# Create your models here.


class RawUFCData(models.Model):
    # Fight information
    date: CharField = models.CharField(max_length=100)
    location: CharField = models.CharField(max_length=100)
    weight_class: CharField = models.CharField(max_length=100)
    title_bout: BooleanField = models.BooleanField()
    winner: CharField = models.CharField(max_length=100)
    red_Fighter: CharField = models.CharField(max_length=100)
    blue_Fighter: CharField = models.CharField(max_length=100)

    # Fight statistics
    red_KD: IntegerField = models.IntegerField()
    blue_KD: IntegerField = models.IntegerField()
    red_Sig_str: IntegerField = models.IntegerField()
    blue_Sig_str: IntegerField = models.IntegerField()
    red_Sig_str_percent: FloatField = models.FloatField()
    blue_Sig_str_percent: FloatField = models.FloatField()
    red_Total_str: IntegerField = models.IntegerField()
    blue_Total_str: IntegerField = models.IntegerField()
    red_Td: IntegerField = models.IntegerField()
    blue_Td: IntegerField = models.IntegerField()
    red_Td_percent: FloatField = models.FloatField()
    blue_Td_percent: FloatField = models.FloatField()
    red_Sub_att: IntegerField = models.IntegerField()
    blue_Sub_att: IntegerField = models.IntegerField()
    red_Rev: IntegerField = models.IntegerField()
    blue_Rev: IntegerField = models.IntegerField()
    red_Ctrl: IntegerField = models.IntegerField()
    blue_Ctrl: IntegerField = models.IntegerField()

    # Red corner fighter details
    red_Height: FloatField = models.FloatField()
    red_Weight: FloatField = models.FloatField()
    red_Reach: FloatField = models.FloatField()
    red_STANCE: CharField = models.CharField(
        max_length=100, default="Orthodox", blank=True
    )
    red_DOB: CharField = models.CharField(max_length=100)
    red_SLpM: FloatField = models.FloatField()
    red_Str_Acc: FloatField = models.FloatField()
    red_SApM: FloatField = models.FloatField()
    red_Str_Def: FloatField = models.FloatField()
    red_TD_Avg: FloatField = models.FloatField()
    red_TD_Acc: FloatField = models.FloatField()
    red_TD_Def: FloatField = models.FloatField()
    red_Sub_Avg: FloatField = models.FloatField()
    red_record: CharField = models.CharField(max_length=100)

    # Blue corner fighter details
    blue_Height: FloatField = models.FloatField()
    blue_Weight: FloatField = models.FloatField()
    blue_Reach: FloatField = models.FloatField()
    blue_STANCE: CharField = models.CharField(
        max_length=100, default="Orthodox", blank=True
    )
    blue_DOB: CharField = models.CharField(max_length=100)
    blue_SLpM: FloatField = models.FloatField()
    blue_Str_Acc: FloatField = models.FloatField()
    blue_SApM: FloatField = models.FloatField()
    blue_Str_Def: FloatField = models.FloatField()
    blue_TD_Avg: FloatField = models.FloatField()
    blue_TD_Acc: FloatField = models.FloatField()
    blue_TD_Def: FloatField = models.FloatField()
    blue_Sub_Avg: FloatField = models.FloatField()
    blue_record: CharField = models.CharField(max_length=100)
