from datetime import datetime
from uuid import uuid4
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from poll.misc_functions import party_symbol_name
from poll.validators import MinAgeValidator

def get_time():
    return datetime.now().timestamp()


class Constituency(models.Model):
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    class Meta:
        db_table = "Constituency"


class Party(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    motto = models.TextField()
    symbol = models.ImageField(upload_to=party_symbol_name)

    class Meta:
        db_table = "Party"

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.symbol:
            self.symbol.delete()
        super(Party, self).delete(*args, **kwargs)


class Candidate(models.Model):
    candidateID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=18)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    criminalRecords = models.BooleanField(default=False)
    count = models.IntegerField(default=0)

    class Meta:
        db_table = "Candidate"

    def __str__(self):
        return self.name


class Voter(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    public_key_n = models.CharField(max_length=320)
    public_key_e = models.IntegerField(default=0)
    birth_date = models.DateField(validators=[MinAgeValidator(18)])
    has_voted = models.BooleanField(default=False)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)

    class Meta:
        db_table = "Voter"

    def __str__(self):
        return self.user.username


class Block(models.Model):
    # id = models.IntegerField(primary_key=True, default=0)
    prev_hash = models.CharField(max_length=64, blank=True)
    merkle_hash = models.CharField(max_length=64, blank=True)
    self_hash = models.CharField(max_length=64, blank=True)
    nonce = models.IntegerField(null=True)
    timestamp = models.FloatField(default=get_time)

    class Meta:
        db_table = "Block"

    def __str__(self):
        return str(self.self_hash)


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    candidate = models.ForeignKey(Candidate, on_delete=models.RESTRICT)
    timestamp = models.FloatField(default=get_time)
    block_id = models.IntegerField(null=True)

    class Meta:
        db_table = "Vote"

    def __str__(self):
        return "{}|{}|{}".format(self.id, self.vote, self.timestamp)


