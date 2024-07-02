from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone

class MedecinManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class Medecin(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    specialite = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    groups = models.ManyToManyField(
        Group,
        related_name='medecin_set',  # Change related_name to avoid clash
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='medecin',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='medecin_set',  # Change related_name to avoid clash
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='medecin',
    )

    objects = MedecinManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Patient(models.Model):

    Nom = models.CharField(max_length=50)
    Prenom = models.CharField(max_length=50)
    Date_Naissance = models.DateField()
    Date_Deces = models.DateField(blank=True,null=True)
    Statut = models.BooleanField(default=False,null=True)
    Date_Debut_P = models.DateField(null=True)
    Date_Fin_P = models.DateField(null=True)
    Groupe_Sanguin = models.CharField(max_length=4,blank=True)
    Menopause = models.CharField(max_length=40,blank=True)
    Type_histo = models.CharField(max_length=40,blank=True)
    Grade_histo = models.CharField(max_length=40,blank=True)
    S_types_moleculaires = models.CharField(max_length=40,blank=True)
    RE = models.CharField(max_length=40,blank=True)
    RP = models.CharField(max_length=40,blank=True)
    HER2 = models.CharField(max_length=40,blank=True)
    KI67 = models.CharField(max_length=40,blank=True)
    Id_M = models.ForeignKey("Medecin",on_delete=models.CASCADE,default=1)

class Traitement_Patient(models.Model):

    Id_P = models.ForeignKey("Patient",on_delete=models.CASCADE,default=0)
    Id_T = models.ForeignKey("Traitement",on_delete=models.CASCADE,default=0)

class Traitement(models.Model):

    Type = models.CharField(max_length=40)

class Consultation(models.Model):

    Date = models.DateField()
    Type = models.CharField(max_length=40)
    Id_P = models.ForeignKey("Patient",on_delete=models.CASCADE,default=0)
   
class Antecedants(models.Model):

    discription = models.CharField(max_length=100)
    Id_P = models.ForeignKey("Patient",on_delete=models.CASCADE,default=0)
