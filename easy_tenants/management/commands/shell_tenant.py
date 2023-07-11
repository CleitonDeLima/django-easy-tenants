from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from easy_tenants import tenant_context, tenant_context_disabled

try:
    from django_extensions.management.commands import shell_plus as shell_cmd
except ImportError:
    from django.core.management.commands import shell as shell_cmd


class Command(BaseCommand):
    help = (
        "Run a Python REPL scoped to a specific tenant. "
        "Specify the --tenant_id or uses --disable to ignore tenant context."
    )
    tests_mode = False

    def add_arguments(self, parser):
        self.cmd = shell_cmd.Command()
        self.cmd.add_arguments(parser)

        parser.add_argument("--tenant_id")
        parser.add_argument(
            "--disable",
            action="store_true",
            help="All tenant are disabled for shell session.",
        )

    def handle(self, *args, **options):
        tenant_id = options.pop("tenant_id", None)
        disable = options.pop("disable", False)

        if disable:
            with tenant_context_disabled():
                self.stdout.write(
                    self.style.SUCCESS(
                        "All tenant are disabled for this shell session "
                        "– please be careful!"
                    )
                )
                return self.call_command(*args, **options)

        TenantModel = apps.get_model(settings.EASY_TENANTS_TENANT_MODEL)
        tenant = TenantModel.objects.get(id=tenant_id)

        with tenant_context(tenant):
            return self.call_command(*args, **options)

    def call_command(self, *args, **options):
        if self.tests_mode:
            return "shell"

        return call_command(self.cmd, *args, **options)
