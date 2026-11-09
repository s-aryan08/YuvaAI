"""
YuvaAI - Usage Service

Tracks daily and per-minute usage
for authenticated users.
"""

from datetime import datetime, timezone, timedelta

from backend.models import UsageRecord, UsageEvent


# ==========================================
# 1. FREE USAGE LIMITS
# ==========================================

DAILY_MESSAGE_LIMIT = 50

PER_MINUTE_LIMIT = 10


# ==========================================
# 2. USAGE EXCEPTION
# ==========================================

class UsageLimitExceeded(Exception):

    def __init__(self, message, limit_type):

        self.message = message

        self.limit_type = limit_type

        super().__init__(message)


# ==========================================
# 3. CHECK AND RECORD USAGE
# ==========================================

def check_and_record_usage(
    db,
    user_id: int
):

    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid authenticated user.")

    now = datetime.now(timezone.utc)

    today = now.date()

    one_minute_ago = now - timedelta(minutes=1)

    # Server-generated identity.
    account_key = f"user:{user_id}"

    try:

        # ==================================
        # CHECK DAILY USAGE
        # ==================================

        daily_record = (
            db.query(UsageRecord)
            .filter(
                UsageRecord.client_id == account_key,
                UsageRecord.usage_date == today
            )
            .first()
        )

        current_daily_count = (
            daily_record.message_count or 0
            if daily_record else 0
        )

        if current_daily_count >= DAILY_MESSAGE_LIMIT:

            raise UsageLimitExceeded(
                "Daily message limit reached. Try again tomorrow.",
                "daily"
            )

        # ==================================
        # CHECK PER-MINUTE USAGE
        # ==================================

        recent_requests = (
            db.query(UsageEvent)
            .filter(
                UsageEvent.client_id == account_key,
                UsageEvent.created_at >= one_minute_ago
            )
            .count()
        )

        if recent_requests >= PER_MINUTE_LIMIT:

            raise UsageLimitExceeded(
                "Too many requests. Please wait a minute.",
                "per_minute"
            )

        # ==================================
        # UPDATE DAILY USAGE
        # ==================================

        if daily_record:

            daily_record.message_count = (
                current_daily_count + 1
            )

        else:

            daily_record = UsageRecord(
                client_id=account_key,
                usage_date=today,
                message_count=1
            )

            db.add(daily_record)

        # ==================================
        # RECORD USAGE EVENT
        # ==================================

        usage_event = UsageEvent(
            client_id=account_key,
            created_at=now
        )

        db.add(usage_event)

        db.commit()

        return {
            "allowed": True,
            "daily_limit": DAILY_MESSAGE_LIMIT,
            "messages_used": daily_record.message_count,
            "messages_remaining": (
                DAILY_MESSAGE_LIMIT -
                daily_record.message_count
            )
        }

    except UsageLimitExceeded:

        db.rollback()

        raise

    except Exception:

        db.rollback()

        raise