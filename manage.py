#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "tienda_musica_project.settings",
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Comprueba que esté instalado "
            "y disponible en el entorno de Python."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
