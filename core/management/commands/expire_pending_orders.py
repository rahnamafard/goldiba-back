from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from core.models import Order, Transaction


class Command(BaseCommand):
    help = 'Removes the unpaid orders after a while and returns balance of reserved products.'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        now = datetime.now()
        offset_in_minutes = 5

        pending_orders = Order.objects.filter(order_status='PE', expired=False)

        for pending_order in pending_orders:
            # ignore recent orders
            if pending_order.created_at >= now - timedelta(minutes=offset_in_minutes):
                continue

            # get order transactions
            have_successful_transaction = pending_order.transactions.filter(status='OK').exists()

            # if the order is not paid, flag it as expired order and return product balances to shop
            if not have_successful_transaction:
                # access middle bridge table for ManyToMany relation to model balances
                for orderModel in pending_order.ordermodel_set.all():
                    model = orderModel.model
                    model.in_stock += orderModel.quantity
                    model.save()

                pending_order.expired = True
                pending_order.save()

        self.stdout.write(self.style.SUCCESS('Unpaid orders has been marked as expired.'))
