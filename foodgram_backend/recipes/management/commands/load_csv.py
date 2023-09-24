import csv
import pathlib
from pathlib import Path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        def csv_to_model(csv_file, model):
            dir_path = pathlib.Path.cwd()
            csv_file_path = Path(dir_path, "data", csv_file)
            with open(csv_file_path, "r", encoding="utf-8") as data_csv_file:
                reader = csv.DictReader(data_csv_file)
                for row in reader:
                    model.objects.create(**row)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Данные успешно загружены из файла "
                        f"{csv_file} в модель {model.__name__}"
                    )
                )

        csv_to_model("ingredients.csv", Ingredient)
