#!/usr/bin/env python
import os
import sys

#IMPORTANT
#Fichier à lancer pour faire tourner la série, permet de vérifier l'installation de Django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SeriePlatform1.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
