from datetime import datetime
from uuid import uuid4

from django.db import models

from poll.misc_functions import party_symbol_name


def get_time():
    return datetime.now().timestamp()


class Constituency(models.Model):
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255)


class Party(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    motto = models.TextField()
    symbol = models.ImageField(upload_to=party_symbol_name)


class Candidate(models.Model):
    candidateID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=18)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    criminalRecords = models.BooleanField(default=False)
    count = models.IntegerField(default=0)


class Voter(models.Model):
    username = models.CharField(max_length=30)
    public_key_n = models.CharField(max_length=320)
    public_key_e = models.IntegerField(default=0)
    has_voted = models.BooleanField(default=False)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    vote = models.IntegerField(default=0)
    timestamp = models.FloatField(default=get_time)
    block_id = models.IntegerField(null=True)

    def __str__(self):
        return "{}|{}|{}".format(self.id, self.vote, self.timestamp)


class Block(models.Model):
    id = models.IntegerField(primary_key=True, default=0)
    prev_hash = models.CharField(max_length=64, blank=True)
    merkle_hash = models.CharField(max_length=64, blank=True)
    self_hash = models.CharField(max_length=64, blank=True)
    nonce = models.IntegerField(null=True)
    timestamp = models.FloatField(default=get_time)

    def __str__(self):
        return str(self.self_hash)
