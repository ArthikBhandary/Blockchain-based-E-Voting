from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Candidate)
admin.site.register(models.Voter)
admin.site.register(models.Vote)
admin.site.register(models.Block)
admin.site.register(models.Constituency)
admin.site.register(models.Party)