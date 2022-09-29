from django.db import models


# Create your models here.
class BankUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64)
    first_name = models.CharField(max_length=128)
    second_name = models.CharField(max_length=128)
    password = models.CharField(max_length=512)
    salt = models.CharField(max_length=16, default="")
    email = models.CharField(max_length=256, default="")
    balance = models.FloatField(default=0.0)
    account_number = models.IntegerField()

    def __str__(self):
        return f"{self.username}: {self.first_name} {self.second_name}"

    class Meta:
        unique_together = ['username', 'email']
