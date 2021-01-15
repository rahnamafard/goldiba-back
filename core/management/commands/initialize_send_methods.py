from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import City, SendMethod, CitySendMethod


class Command(BaseCommand):
    help = 'Creates send methods and assign them to cities.'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        # 1) create `post` and assign to all cities
        post = SendMethod.objects.create(label='پست',
                                         price=20000)
        cities = City.objects.all()
        for city in cities:
            CitySendMethod.objects.create(city=city,
                                          send_method=post)

        # 2) create `alopeyk` and assign to `تهران`
        alopeyk = SendMethod.objects.create(label='الوپیک (تهران)',
                                            price=0,
                                            alternative_price_text='پرداخت هنگام تحویل')
        tehran = City.objects.get(name="تهران")
        CitySendMethod.objects.create(city=tehran,
                                      send_method=alopeyk)

        # 3) create `hozouri` and assign to `تهران`
        hozouri = SendMethod.objects.create(label='تحویل حضوری (تهران)',
                                            price=0,
                                            alternative_price_text='توسط خریدار در گالری')
        CitySendMethod.objects.create(city=tehran,
                                      send_method=hozouri)

        # Print success message
        self.stdout.write(self.style.SUCCESS('All send methods were created and assigned to their cities.'))
