from django.core.files.uploadedfile import SimpleUploadedFile

from easy_tenants.storage import TenantFileSystemStorage


def test_default_storage(tenant_ctx, settings):
    tenant_id = str(tenant_ctx.id)
    s = TenantFileSystemStorage()
    file = SimpleUploadedFile('test.txt', b'any content')
    s.save('test.txt', file)

    assert s.exists('test.txt')
    assert s.path('test.txt') == f'{settings.MEDIA_ROOT}/{tenant_id}/test.txt'
    assert s.url('test.txt') == f'{settings.MEDIA_URL}{tenant_id}/test.txt'
