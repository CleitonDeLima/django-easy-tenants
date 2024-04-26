import re
import sys

from django.conf import settings
from django.urls import URLResolver

from easy_tenants import get_current_tenant
from easy_tenants.exceptions import TenantError


class TenantPrefixPattern:
    converters = {}

    @property
    def tenant_prefix(self):
        try:
            tenant = get_current_tenant()
            return f"{tenant.id}/"
        except TenantError:
            return "/"

    @property
    def regex(self):
        # This is only used by reverse() and cached in _reverse_dict.
        # Note: This caching must actually be bypassed elsewhere in order to effectively switch tenants.
        return re.compile(self.tenant_prefix)

    def match(self, path):
        tenant_prefix = self.tenant_prefix
        if path.startswith(tenant_prefix):
            return path[len(tenant_prefix) :], (), {}
        return None

    def check(self):
        return []

    def describe(self):
        return "'{}'".format(self)

    def __str__(self):
        return self.tenant_prefix


def tenant_patterns(urls: list):
    """
    Add the tenant prefix to every URL pattern within this function.
    This may only be used in the root URLconf, not in an included URLconf.
    """
    return [URLResolver(TenantPrefixPattern(), urls)]


def get_dynamic_tenant_suffixed_urlconf(urlconf, dynamic_path):
    """
    Generates a new URLConf module with all patterns prefixed with tenant.
    """
    from types import ModuleType

    from django.utils.module_loading import import_string

    class LazyURLConfModule(ModuleType):
        def __getattr__(self, attr):
            urlpatterns = import_string("{}.{}".format(urlconf, attr))
            root_urls = import_string(f"{settings.ROOT_URLCONF}.{attr}")
            if attr == "urlpatterns":
                return root_urls + tenant_patterns(urlpatterns)
            return urlpatterns

    return LazyURLConfModule(dynamic_path)


def get_subfolder_urlconf(tenant):
    """
    Creates and returns a suffixed URLConf for tenant.
    """
    urlconf = "tenant_urls"
    dynamic_path = urlconf + "_dynamically_suffixed"
    if not sys.modules.get(dynamic_path):
        sys.modules[dynamic_path] = get_dynamic_tenant_suffixed_urlconf(
            urlconf, dynamic_path
        )
    return dynamic_path
