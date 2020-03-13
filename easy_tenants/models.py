from django.conf import settings
from django.db import models


class TenantAbstract(models.Model):
    tenant = models.ForeignKey(
        to=settings.TENANT_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
