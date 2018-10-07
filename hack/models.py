from django.db import models

# Create your models here.
class Meeting(models.Model):
    leader_name = models.CharField(max_length=50)
    agenda = models.TextField()
    date = models.CharField(max_length=50)
    transcripts = models.TextField()
    summary = models.TextField(null=True)
    no_of_persons = models.IntegerField(default=2)

    def __str__(self):
        return str(self.leader_name)
