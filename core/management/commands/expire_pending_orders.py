from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from core.models import Order


class Command(BaseCommand):
    help = 'Removes the unpaid orders after a while and returns balance of reserved products.'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        i = 0
        now = datetime.now()
        online_offset_minutes = 60
        offline_offset_days = 1

        pending_orders = Order.objects.filter(order_status='PE')

        for pending_order in pending_orders:

            # get order transactions
            successful_transactions = pending_order.transactions.filter(status='OK')
            offline_pending_transactions = pending_order.transactions.filter(method='OF', status='PE')
            # online_pending_transactions = pending_order.transactions.filter(~Q(method='OF'), status='PE')

            # if the order is not paid, flag it as expired order and return product balances to shop
            if not successful_transactions.exists():

                # ignore orders having transactions from m minutes ago
                if pending_order.created_at >= now - timedelta(minutes=online_offset_minutes):
                    print(pending_order.tracking_code + " ignored (1).")
                    continue

                # ignore orders having pending offline transaction from n days ago
                if offline_pending_transactions.exists():
                    if pending_order.created_at >= now - timedelta(days=offline_offset_days):
                        print(pending_order.tracking_code + " ignored (2).")
                        continue

                # access middle bridge table for ManyToMany relation to model balances
                for orderModel in pending_order.ordermodel_set.all():
                    model = orderModel.model
                    model.in_stock += orderModel.quantity
                    model.save()

                i += 1
                pending_order.order_status = 'EX'
                pending_order.save()
                print(pending_order.tracking_code + " expired.")

            elif pending_order.order_status != 'AP':
                pending_order.order_status = 'AP'
                pending_order.save()

        self.stdout.write(self.style.SUCCESS(str(i) + ' orders has been marked as expired.'))
