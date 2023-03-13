from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    pass


class DynamicField(models.Model):
    VALUE_CHOICES = (
        ("Number", "Number"),
        ("Text", "Text"),
    )
    content_type = models.ForeignKey(ContentType, null=True,
                                     on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True)
    object = GenericForeignKey()
    field_name = models.CharField(max_length=255, unique=True)
    value_type = models.CharField(choices=VALUE_CHOICES, max_length=6)
    is_mandatory = models.BooleanField(default=False)
    length = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.field_name = self.field_name.lower()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.field_name + " -> " + self.value_type


def validate_dynamic_fields(**kwargs):
    # kwargs contains all the data required for mapping the dynamic field of given model
    force_insert = kwargs.pop('force_insert')
    if not all(kwargs.values()):
        assert "Values cannot be null."

    model_name = kwargs.get('model_name')
    field_name = kwargs.get('field_name')
    field_value = kwargs.get('field_value')
    klass = kwargs.get('klass')
    fil = {
        kwargs.get('base_instance_field'): kwargs.get('base_instance')
    }

    dynamic_field = DynamicField.objects.filter(
        content_type__model=model_name,
        field_name=field_name
    ).first()

    def raise_validation_error(message: str):
        raise ValidationError({field_name: message})

    if not dynamic_field:
        raise_validation_error("Field not found.")

    if len(field_value) > dynamic_field.length:
        raise_validation_error("This field length exceeded maximum limit.")

    if dynamic_field.value_type == "Number":
        try:
            float(field_value)
        except ValueError:
            raise_validation_error("Expected number but got different type.")

    if dynamic_field.is_mandatory and not field_value:
        raise_validation_error("This field may not be null.")

    if klass.objects.filter(
            **fil,
            field_name=field_name
    ).exists() and force_insert:
        raise_validation_error("This field already exists.")


class DynamicModelFieldMap(models.Model):
    field_name = models.CharField(max_length=255)
    field_value = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class UserField(DynamicModelFieldMap):
    user = models.ForeignKey(User, related_name='user_fields', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # data required for validating dynamic fields before save
        data = {
            "base_instance": self.user,
            "base_instance_field": "user",
            "model_name": self.user._meta.verbose_name,
            "field_name": self.field_name,
            "field_value": self.field_value,
            "klass": UserField,
            "force_insert": kwargs.get('force_insert', False)
        }
        validate_dynamic_fields(**data)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.user + " -> " + self.field_name
