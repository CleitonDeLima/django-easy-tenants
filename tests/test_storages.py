from django.core.files.uploadedfile import SimpleUploadedFile

from easy_tenants import tenant_context_disabled
from easy_tenants.storage import TenantFileSystemStorage


def test_default_storage(tenant_ctx, settings):
    tenant_id = str(tenant_ctx.id)
    s = TenantFileSystemStorage()
    file = SimpleUploadedFile("test.txt", b"any content")
    s.save("test.txt", file)

    assert s.exists("test.txt")
    assert s.path("test.txt") == f"{settings.MEDIA_ROOT}/{tenant_id}/test.txt"
    assert s.url("test.txt") == f"{settings.MEDIA_URL}{tenant_id}/test.txt"


def test_default_storage_without_tenant(settings):
    with tenant_context_disabled():
        s = TenantFileSystemStorage()
        file = SimpleUploadedFile("test.txt", b"any content")
        s.save("test.txt", file)

        assert s.exists("test.txt")
        assert s.path("test.txt") == f"{settings.MEDIA_ROOT}/test.txt"
        assert s.url("test.txt") == f"{settings.MEDIA_URL}test.txt"


def test_custom_base_location(tenant_ctx, settings):
    location = f"{settings.MEDIA_ROOT}/2"
    s = TenantFileSystemStorage(location=location, base_url="custom_url")
    file = SimpleUploadedFile("test.txt", b"any content")
    s.save("test.txt", file)
    assert s.exists("test.txt")
    assert s.path("test.txt") == f"{location}/test.txt"
    assert s.url("test.txt") == "custom_url/test.txt"
