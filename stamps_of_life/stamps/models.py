import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, name, password, **kwargs):
        kwargs.setdefault('is_admin', False)
        if not email:
            raise ValueError('이메일은 필수입니다.')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.name = name
        return user

    def create_superuser(self, email, name, password, **kwargs):
        kwargs.setdefault('is_admin', True)
        if not email:
            raise ValueError('이메일은 필수입니다.')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.name = name
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )
    email = models.EmailField(unique=True, verbose_name='이메일')
    name = models.CharField(max_length=20, verbose_name='이름')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='가입일')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    is_admin = models.BooleanField(default=False, verbose_name='관리자 여부')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    class Meta:
        verbose_name ='사용자'
        verbose_name_plural = '사용자'

    @property
    def is_staff(self):
        return self.is_admin


class Board(models.Model):
    objects = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=32, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def __str__ (self):
        return self.name

class Stamp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    count = models.IntegerField(default=0)
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=32, default='normal')
    def __str__(self):
        return self.name

class CLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE)
    stamped_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.stamp.name



