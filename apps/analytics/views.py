"""
apps/analytics/views.py
"""
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Sum, Count, Avg, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


def _require_admin(user):
    """Your app uses role='admin', not is_staff. Check that instead."""
    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    if getattr(user, 'role', None) != 'admin':
        raise PermissionDenied("Admin access required.")


def _period_bounds(period: str):
    today = timezone.now().date()
    if period == "yearly":
        cur_start  = today.replace(month=1, day=1)
        cur_end    = today
        prev_start = cur_start - relativedelta(years=1)
        prev_end   = cur_start - timedelta(days=1)
    elif period == "quarterly":
        q_start_month = ((today.month - 1) // 3) * 3 + 1
        cur_start  = today.replace(month=q_start_month, day=1)
        cur_end    = today
        prev_start = cur_start - relativedelta(months=3)
        prev_end   = cur_start - timedelta(days=1)
    else:  # monthly
        cur_start  = today.replace(day=1)
        cur_end    = today
        prev_start = cur_start - relativedelta(months=1)
        prev_end   = cur_start - timedelta(days=1)
    return cur_start, cur_end, prev_start, prev_end


def _pct_change(current, previous):
    if not previous:
        return "+100%" if current else "0%"
    change = ((current - previous) / previous) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.1f}%"


class AnalyticsMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _require_admin(request.user)

        from apps.payments.models import Payment
        from apps.bookings.models import Booking
        from apps.accounts.models import User

        period = request.query_params.get("period", "monthly")
        cur_start, cur_end, prev_start, prev_end = _period_bounds(period)

        def revenue_in(start, end):
            result = Payment.objects.filter(
                status="completed",
                created_at__date__gte=start,
                created_at__date__lte=end,
            ).aggregate(total=Sum("amount"))["total"] or 0
            return float(result)

        cur_rev  = revenue_in(cur_start, cur_end)
        prev_rev = revenue_in(prev_start, prev_end)

        def bookings_in(start, end):
            return Booking.objects.filter(
                status__in=["completed", "confirmed", "in_progress"],
                created_at__date__gte=start,
                created_at__date__lte=end,
            ).count()

        cur_book  = bookings_in(cur_start, cur_end)
        prev_book = bookings_in(prev_start, prev_end)

        cur_avg  = round(cur_rev  / cur_book,  2) if cur_book  else 0
        prev_avg = round(prev_rev / prev_book, 2) if prev_book else 0

        def new_clients_in(start, end):
            return User.objects.filter(
                role="customer",
                date_joined__date__gte=start,
                date_joined__date__lte=end,
            ).count()

        cur_clients  = new_clients_in(cur_start, cur_end)
        prev_clients = new_clients_in(prev_start, prev_end)

        period_label = period.capitalize()
        return Response([
            {
                "label":  "Total Revenue",
                "value":  f"${cur_rev:,.2f}",
                "raw":    cur_rev,
                "change": _pct_change(cur_rev, prev_rev),
                "period": f"This {period_label}",
            },
            {
                "label":  "Bookings",
                "value":  str(cur_book),
                "raw":    cur_book,
                "change": _pct_change(cur_book, prev_book),
                "period": f"This {period_label}",
            },
            {
                "label":  "Avg. Booking Value",
                "value":  f"${cur_avg:,.2f}",
                "raw":    cur_avg,
                "change": _pct_change(cur_avg, prev_avg),
                "period": f"This {period_label}",
            },
            {
                "label":  "New Clients",
                "value":  str(cur_clients),
                "raw":    cur_clients,
                "change": _pct_change(cur_clients, prev_clients),
                "period": f"This {period_label}",
            },
        ])


class RevenueTrendView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _require_admin(request.user)

        from apps.payments.models import Payment

        period = request.query_params.get("period", "monthly")
        today  = timezone.now().date()

        if period == "yearly":
            n_periods  = 3
            trunc_fn   = TruncYear
            label_fmt  = lambda d: str(d.year)
            delta      = relativedelta(years=1)
            start_date = today.replace(month=1, day=1) - relativedelta(years=n_periods - 1)
        elif period == "quarterly":
            n_periods  = 4
            trunc_fn   = TruncQuarter
            label_fmt  = lambda d: f"Q{((d.month - 1) // 3) + 1} {d.year}"
            delta      = relativedelta(months=3)
            q_month    = ((today.month - 1) // 3) * 3 + 1
            start_date = today.replace(month=q_month, day=1) - relativedelta(months=3 * (n_periods - 1))
        else:
            n_periods  = 6
            trunc_fn   = TruncMonth
            label_fmt  = lambda d: d.strftime("%b")
            delta      = relativedelta(months=1)
            start_date = today.replace(day=1) - relativedelta(months=n_periods - 1)

        qs = (
            Payment.objects
            .filter(status="completed", created_at__date__gte=start_date)
            .annotate(bucket=trunc_fn("created_at"))
            .values("bucket")
            .annotate(revenue=Sum("amount"))
            .order_by("bucket")
        )

        rev_map = {row["bucket"].date(): float(row["revenue"]) for row in qs}

        result = []
        cursor = start_date
        for _ in range(n_periods):
            result.append({"label": label_fmt(cursor), "revenue": rev_map.get(cursor, 0)})
            cursor += delta

        return Response(result)


class TopServicesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _require_admin(request.user)

        from apps.bookings.models import BookingItem

        period = request.query_params.get("period", "monthly")
        cur_start, cur_end, *_ = _period_bounds(period)

        qs = (
            BookingItem.objects
            .filter(
                booking__payment__status="completed",
                booking__payment__created_at__date__gte=cur_start,
                booking__payment__created_at__date__lte=cur_end,
            )
            .values(name=F("service__name"))
            .annotate(
                revenue=Sum(
                    ExpressionWrapper(
                        F("price_at_time") * F("quantity"),
                        output_field=DecimalField(),
                    )
                ),
                bookings=Count("booking", distinct=True),
            )
            .order_by("-revenue")[:5]
        )

        services = [
            {
                "name":     row["name"] or "Unknown Service",
                "revenue":  float(row["revenue"]),
                "bookings": row["bookings"],
            }
            for row in qs
        ]

        max_rev = services[0]["revenue"] if services else 1
        for s in services:
            s["pct"] = round((s["revenue"] / max_rev) * 100) if max_rev else 0

        return Response(services)


class StaffPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _require_admin(request.user)

        from apps.payments.models import Payment
        from apps.reviews.models import Review

        period = request.query_params.get("period", "monthly")
        cur_start, cur_end, *_ = _period_bounds(period)

        perf_qs = (
            Payment.objects
            .filter(
                status="completed",
                created_at__date__gte=cur_start,
                created_at__date__lte=cur_end,
                booking__worker__isnull=False,
            )
            .values(
                worker_id=F("booking__worker__id"),
                first_name=F("booking__worker__user__first_name"),
                last_name=F("booking__worker__user__last_name"),
            )
            .annotate(
                revenue=Sum("amount"),
                bookings=Count("id"),
            )
            .order_by("-revenue")[:10]
        )

        rating_qs = (
            Review.objects
            .filter(is_approved=True)
            .values("worker_id")
            .annotate(avg_rating=Avg("rating"))
        )
        rating_map = {row["worker_id"]: float(row["avg_rating"]) for row in rating_qs}

        PALETTE = [
            "bg-rose-100 text-rose-700",
            "bg-blue-100 text-blue-700",
            "bg-emerald-100 text-emerald-700",
            "bg-amber-100 text-amber-700",
            "bg-purple-100 text-purple-700",
            "bg-cyan-100 text-cyan-700",
        ]

        result = []
        for i, row in enumerate(perf_qs):
            first     = row["first_name"] or ""
            last      = row["last_name"]  or ""
            full_name = f"{first} {last}".strip() or "Unknown"
            initials  = (first[:1] + last[:1]).upper() or "??"
            wid       = row["worker_id"]

            result.append({
                "id":       str(wid),
                "name":     full_name,
                "initials": initials,
                "revenue":  float(row["revenue"]),
                "bookings": row["bookings"],
                "rating":   round(rating_map.get(wid, 0), 1),
                "color":    PALETTE[i % len(PALETTE)],
            })

        return Response(result)