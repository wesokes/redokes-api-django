from django.db import models


class User(models.Model):
    """
    User model
    """
    email = models.CharField(max_length=256)


class Organization(models.Model):
    """
    Organization model
    """
    name = models.CharField(max_length=64)


class Team(models.Model):
    """
    Team model
    """
    name = models.CharField(max_length=64)
    organization = models.ForeignKey(Organization)


class Account(models.Model):
    """
    Account model
    """
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    team = models.ForeignKey(Team)
    organization = models.ForeignKey(Organization)


class Order(models.Model):
    """
    Order model
    """
    account = models.ForeignKey(Account)
    revenue = models.FloatField()
    margin = models.FloatField()
    cost = models.FloatField()
    time = models.DateTimeField()
