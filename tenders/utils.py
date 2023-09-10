import asyncio

import httpx

from tenders.db_utils import check_tender_exists, update_tender, save_tender
from tenders.models import Tender

DETAIL_API_URL = "https://public.api.openprocurement.org/api/0/tenders/"
BATCH_SIZE = 10

""" Fetch information about tenders from the specified API URL. """


async def get_tenders_info_all(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        tasks = []

        for item in data["data"][:BATCH_SIZE]:
            if not await check_tender_exists(item["id"]):
                tasks.append(fetch_tender_details(item["id"], client))
            else:
                tasks.append(
                    fetch_tender_details(item["id"], client, update=True)
                )

        await asyncio.gather(*tasks)


""" Fetch details of a tender from the API and update the database. """


async def fetch_tender_details(tender_id, client, update=False):
    tender_page = await client.get(f"{DETAIL_API_URL}{tender_id}")
    tender_page.raise_for_status()
    tender_data = tender_page.json()

    date_modified = tender_data["data"]["dateModified"]
    amount = tender_data["data"]["value"]["amount"] or 0
    description = tender_data["data"].get("description") or "Опис не надано"

    if update:
        await update_tender(tender_id, date_modified, amount, description)
    else:
        tender = Tender(
            tender_id=tender_id,
            date_modified=date_modified,
            amount=amount,
            description=description,
        )
        await save_tender(tender)
