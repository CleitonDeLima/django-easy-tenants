import os
from contextlib import suppress
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from easy_tenants import get_current_tenant


class TenantFileSystemStorage(FileSystemStorage):
    """
    Standard filesystem tenant storage
    """

    def get_relative_tenant_location(self):
        with suppress(AttributeError):
            tenant = get_current_tenant()
            return os.path.join(settings.MEDIA_ROOT, str(tenant.id))

        return settings.MEDIA_ROOT

    def get_relative_tenant_url(self):
        with suppress(AttributeError):
            tenant = get_current_tenant()
            return urljoin(settings.MEDIA_URL, str(tenant.id) + "/")

        return settings.MEDIA_URL

    @property
    def base_location(self):  # Not cached like in parent class
        return self._value_or_setting(
            self._location, self.get_relative_tenant_location()
        )

    @property
    def location(self):  # Not cached like in parent class
        return os.path.abspath(self.base_location)

    @property
    def base_url(self):  # Not cached like in parent class
        if self._base_url is not None and not self._base_url.endswith("/"):
            self._base_url += "/"

        return self._value_or_setting(
            self._base_url, self.get_relative_tenant_url()
        )
