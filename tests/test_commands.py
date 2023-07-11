from io import StringIO

import pytest
from django.core.management import call_command

from easy_tenants.management.commands import shell_tenant
from tests.models import StoreTenant


@pytest.mark.django_db
class TestShellTenant:
    def test_set_tenant_context(self):
        tenant = StoreTenant.objects.create()

        cmd = shell_tenant.Command()
        cmd.tests_mode = True

        assert call_command(cmd, tenant_id=str(tenant.id)) == "shell"

    def test_override(self):
        stdout = StringIO()
        cmd = shell_tenant.Command()
        cmd.tests_mode = True

        call_command(cmd, "--disable", stdout=stdout)
        assert (
            "All tenant are disabled for this shell session – "
            "please be careful!"
        ) in stdout.getvalue()
