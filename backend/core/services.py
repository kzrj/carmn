from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from core.models import ExchangeRate


def get_health_payload() -> dict:
    return {
        "status": "ok",
        "server_time": timezone.now().isoformat(),
    }


def get_exchange_rate(currency: str = "USD", on_date: date | None = None) -> Decimal | None:
    target_date = on_date or timezone.localdate()
    rate = (
        ExchangeRate.objects.filter(currency=currency.upper(), date__lte=target_date)
        .order_by("-date")
        .values_list("rate_to_mnt", flat=True)
        .first()
    )
    return rate


def convert_usd_to_mnt(amount_usd: Decimal, on_date: date | None = None) -> int:
    rate = get_exchange_rate("USD", on_date)
    if rate is None:
        raise ValueError("USD exchange rate is not configured.")
    mnt = (amount_usd * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(mnt)


def resolve_listing_price(
    *,
    price: int | None,
    price_usd: Decimal | None,
    fallback_price: int | None = None,
    fallback_price_usd: Decimal | None = None,
) -> tuple[int, Decimal | None]:
    if price is not None and price > 0:
        return price, price_usd if price_usd is not None else fallback_price_usd
    if price_usd is not None and price_usd > 0:
        return convert_usd_to_mnt(price_usd), price_usd
    if fallback_price is not None and fallback_price > 0:
        return fallback_price, fallback_price_usd
    raise ValueError("Either price (MNT) or price_usd must be provided.")
