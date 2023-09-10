from asgiref.sync import sync_to_async
from django.db import transaction


from tenders.models import Tender

""" Check if a tender with the given ID exists in the database. """


@sync_to_async
def check_tender_exists(tender_id):
    return Tender.objects.filter(tender_id=tender_id).exists()


""" Save a tender object to the database. """


@sync_to_async
@transaction.atomic
def save_tender(tender):
    tender.save()


""" Update an existing tender's information in the database
if it has changed since the last update.
It takes additional time to check if the information has changed,
but it is necessary to avoid """


@sync_to_async
@transaction.atomic
def update_tender(tender_id, date_modified, amount, description):
    tender = Tender.objects.get(tender_id=tender_id)

    if tender.date_modified != date_modified or tender.amount != amount or tender.description != description:
        tender.date_modified = date_modified
        tender.amount = amount
        tender.description = description
        tender.save()
