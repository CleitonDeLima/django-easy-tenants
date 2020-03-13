from django.conf import settings


def pytest_configure():
    settings.configure(
        SECRET_KEY='any-key',
        ROOT_URLCONF='tests.urls',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'tests',
        ],
        TENANT_MODEL='tests.StoreTenant'
    )
