import uuid
from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from easy_tenants.management.commands import shell_tenant
from tests.models import StoreTenant, Warehouse


@pytest.mark.django_db
class TestShellTenant:
    def test_set_tenant_context(self):
        tenant = StoreTenant.objects.create()

        cmd = shell_tenant.Command()
        cmd.tests_mode = True

        assert call_command(cmd, tenant_id=str(tenant.id)) == "shell"

    def test_run_shell_in_tenant_context(self, capsys):
        tenant = StoreTenant.objects.create()

        call_command(
            "shell_tenant",
            tenant_id=str(tenant.id),
            command="from easy_tenants import get_current_tenant; "
            "print(get_current_tenant().pk)",
        )

        assert str(tenant.pk) in capsys.readouterr().out

    def test_tenant_without_id_field(self, settings):
        settings.EASY_TENANTS_TENANT_MODEL = "tests.Warehouse"
        Warehouse.objects.create(code="w1", slug="first")

        cmd = shell_tenant.Command()
        cmd.tests_mode = True

        assert call_command(cmd, tenant_id="w1") == "shell"

    def test_missing_tenant_id(self):
        cmd = shell_tenant.Command()
        cmd.tests_mode = True

        with pytest.raises(CommandError, match="--tenant_id or --disable"):
            call_command(cmd)

    @pytest.mark.parametrize("tenant_id", ["not-a-uuid", str(uuid.uuid4())])
    def test_tenant_not_found(self, tenant_id):
        cmd = shell_tenant.Command()
        cmd.tests_mode = True

        with pytest.raises(CommandError, match="not found"):
            call_command(cmd, tenant_id=tenant_id)

    def test_override(self):
        stdout = StringIO()
        cmd = shell_tenant.Command()
        cmd.tests_mode = True

        call_command(cmd, "--disable", stdout=stdout)
        assert (
            "All tenant are disabled for this shell session – "
            "please be careful!"
        ) in stdout.getvalue()
