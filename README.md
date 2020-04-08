# easy-tenants

![Tests](https://github.com/CleitonDeLima/django-easy-tenants/workflows/Tests/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/CleitonDeLima/django-easy-tenants/badge.svg?branch=github-ci)](https://coveralls.io/github/CleitonDeLima/django-easy-tenants?branch=github-ci)
[![PyPI Version](https://img.shields.io/pypi/v/django-easy-tenants.svg)](https://pypi.org/project/django-easy-tenants/)
[![PyPI downloads](https://img.shields.io/pypi/dm/django-easy-tenants.svg)](https://img.shields.io/pypi/dm/django-easy-tenants.svg)

Este projeto tem como objetivo dar suporte a multiplos inquilinos para uma 
aplicação django. 
 
Normalmente, existem três soluções para resolver o problema de multiplos inquilinos:

1. Isolada: bancos de dados separados. Cada inquilino possui seu próprio banco de dados.
2. Semi-Isolada: Banco de Dados Compartilhado, Esquemas Separados. Um banco de dados para todos os inquilinos, 
mas um esquema para cada inquilino.
3. Compartilhada: banco de dados compartilhado, esquema compartilhado. 
Todos os inquilinos compartilham o mesmo banco de dados e esquema. Há uma tabela de inquilino principal, na qual 
todas as outras tabelas têm uma chave estrangeira apontando para cada inquilino.

Esta aplicação implementa a terceira solução, que em nossa opinião, é a melhor abordagem para suportar um número
grande de inquilinos.

Para mais informações: [Building Multi Tenant Applications with Django
](https://books.agiliq.com/projects/django-multi-tenant/en/latest/)

Segue um exemplo de cada solução considerando 5000 inquilinos: 

Solução       | Quantidade DB | Quantidade Esquemas | Tempo de migração      | Acesso publico
------------- | ------------- | ------------------- | ---------------------- | ---------------
Isolada       | 5000          | 1 por DB            | demorado (1 x DB)      | Não
Semi-Isolada  | 1             | 5000                | demorado (1 x esquema) | Sim
Compartilhada | 1             | 1                   | rápido (1x)            | Sim


## Como funciona
![how to works](./screenshots/flux_easy_tenants.png) 


## Instalação
É aconcelhavel fazer a instalação no inicio de um projeto. Em um projeto já existente,
depedendo da estrutura dos modelos, pode ser dificil a migração dos dados.

Adicione `easy_tenant` em seu `INSTALLED_APPS` no settings.py:

```python
INSTALLED_APPS = [
    ...,
    'easy_tenants',
]
```
   
É preciso criar um modelo que será o inquilino da aplicação, em seus settings adicione 
`EASY_TENANTS_MODEL`:

`yourapp/models.py`
```python
from easy_tenants.models import TenantMixin

class Customer(TenantMixin):
    ...
```

`settings.py`
```python
EASY_TENANTS_MODEL = 'yourapp.CustomModel'
```

Seus modelos que serão isolado por inquilino devem herdar de `TenantAbstract` e usar o manager `TenantManager`:

```python
from django.db import models
from easy_tenants.models import TenantAbstract
from easy_tenants.managers import TenantManager

class Product(TenantAbstract):
    name = models.CharField(max_length=10)

    objects = TenantManager()
```

É preciso definir o middleware `easy_tenants.middleware.DefaultTenantMiddleware` no settings:  
_deve vir depois do `django.contrib.auth.middleware.AuthenticationMiddleware`_

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'easy_tenants.middleware.DefaultTenantMiddleware',
]
```

Inclua a url:

```python
path('easy-tenants/', include('easy_tenants.urls')),
```

É preciso criar uma view que irá listar todos os seus tenants e depois incluir o nome
dessa view no settings. Isso server para definir um tenant na sessão do usuário.


`views.py`
```python
from django.shortcuts import render

def tenant_list(request):
    user_tenants = request.user.tenants.all()
    return render(request, 'tenant_list.html', {
        'object_list': user_tenants
    })
```

`tenant_list.html`
```html
...
<ul>
  {% for object in object_list %}
    <li>
      <form action="{% url 'easy_tenants:set-current-tenant' object.pk %}" method="post">
        {% csrf_token %}
        <button type="submit">Use {{ object.name }}</button>
      </form>
    </li>
  {% endfor %}
</ul>
...
```

`urls.py`
```python
path('tenants/', tenant_list, name='tenant-list'),
```

`settings.py`
```python
EASY_TENANTS_LIST_URL = 'tenant-list'
```

Depois de escolher o tenant, o usuário é redirecionado para uma url definida 
no settings `EASY_TENANTS_REDIRECT_URL`:

`settings.py`
```python
EASY_TENANTS_REDIRECT_URL = 'home'
```  


Caso não houver um tenant definido na sessão, toda url é é redirecionada para 
`EASY_TENANTS_LIST_URL`, se deseja ignorar algumas urls é possivel informar o nome
delas na configuração `EASY_TENANTS_IGNORE_URLS`, conforme o exemplo:

```python
EASY_TENANTS_IGNORE_URLS = [
    'admin:index',
    'admin:login',
    'namespace:url_name',
]
```

Caso queira separar os arquivos de upload por tenant, basta mudar a configuração `DEFAULT_FILE_STORAGE`
(disponivel somente para arquivos locais):

```python
DEFAULT_FILE_STORAGE = 'easy_tenants.storage.TenantFileSystemStorage'
```


## Excutar o projeto de exemplo
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Acesse a pagina `/admin/`, crie um `Customer` e adicione o usuário a ele.

## Inspiração
[django-tenant-schemas](https://github.com/bernardopires/django-tenant-schemas)  
[django-tenants](https://github.com/tomturner/django-tenants)  
[django-scopes](https://github.com/raphaelm/django-scopes)  
