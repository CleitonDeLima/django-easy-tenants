# Example project

The repository contains an example project in `example/`. From the
repository root, with the package installed:

```bash
python -m pip install -e . -r example/requirements.txt
cd example
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `/admin/`, log in and create a `Customer`. Then open `/`, choose the
customer and create categories and products for it.
