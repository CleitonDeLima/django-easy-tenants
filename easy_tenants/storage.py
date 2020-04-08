from contextlib import suppress

from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join

from easy_tenants import get_current_tenant


class TenantFileSystemStorage(FileSystemStorage):
    """
    Standard filesystem tenant storage
    """

    def path(self, name):
        """
        Return a local filesystem path joined with a tenant context
        """
        try:
            tenant = get_current_tenant()
            # TODO: Change tenant attr with function
            location = safe_join(self.location, str(tenant.id))
        except AttributeError:
            location = self.location

        path = safe_join(location, name)

        return path

    def url(self, name):
        """
        Return an absolute URL joined with a tenant context where the file's
        contents can be accessed directly by a Web browser.
        """
        with suppress(AttributeError):
            tenant = get_current_tenant()
            # TODO: Change tenant attr with function
            name = '{0}/{1}'.format(str(tenant.id), name)

        return super().url(name)
