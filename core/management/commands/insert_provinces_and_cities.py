import json
from django.core.management.base import BaseCommand

from core.models import Province, City


class Command(BaseCommand):
    help = 'Inserts list of provinces and cities into database.'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        # Open json file
        json_file = open('core/management/commands/iran_provinces_and_cities.json', encoding="utf8")

        # Load json file to `data`
        data = json.load(json_file)

        # Iterate through `data`
        for province in data['provinces']:
            province_instance = Province(name=province['name'])
            province_instance.save()
            for city in province['cities']:
                city_instance = City(name=city['name'])
                city_instance.province = province_instance  # assign city to its province
                city_instance.save()

        # Closing json file
        json_file.close()

        # Print success message
        self.stdout.write(self.style.SUCCESS('All provinces and their cities were inserted into database.'))
