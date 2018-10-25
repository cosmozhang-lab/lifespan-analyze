from django.db import models

class User(models.Model):
    username = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128)

class Dataset(models.Model):
    setname = models.CharField(max_length=32, unique=True)

class Sample(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    seq = models.IntegerField()
    plate = models.CharField(max_length=4)
    rootdir = models.CharField(max_length=256)
    subdir = models.CharField(max_length=256)
    filename = models.CharField(max_length=256)
    STATUS_UNMARKED = 0
    STATUS_PENDING = 1
    STATUS_MARKED = 2
    STATUS_CHOICES = (
            (STATUS_UNMARKED, "Unmarked"),
            (STATUS_PENDING, "Pending"),
            (STATUS_MARKED, "Marked")
        )
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_UNMARKED)
    marker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
