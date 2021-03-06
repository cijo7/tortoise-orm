from datetime import date, datetime, timedelta, timezone
from time import sleep

from iso8601 import ParseError

from tests import testmodels
from tortoise import fields
from tortoise.contrib import test
from tortoise.exceptions import ConfigurationError, IntegrityError


class TestDatetimeFields(test.TestCase):
    def test_both_auto_bad(self):
        with self.assertRaisesRegex(
            ConfigurationError, "You can choose only 'auto_now' or 'auto_now_add'"
        ):
            fields.DatetimeField(auto_now=True, auto_now_add=True)

    def test_timezone_aware_bad(self):
        with self.assertRaisesRegex(
            ConfigurationError, "Please specify a valid timezone to both 'tz' and 'db_tz'"
        ):
            fields.DatetimeField(tz=None, db_tz=timezone(timedelta(hours=5)))
        with self.assertRaisesRegex(
            ConfigurationError, "Please specify a valid timezone to both 'tz' and 'db_tz'"
        ):
            fields.DatetimeField(tz=timezone(timedelta(hours=5)), db_tz=None)

    async def test_empty(self):
        with self.assertRaises(IntegrityError):
            await testmodels.DatetimeFields.create()

    async def test_create(self):
        utc_now = datetime.utcnow()
        tz = timezone(timedelta(hours=3))
        now = datetime.now(tz)
        auto_now = datetime.now()
        obj0 = await testmodels.DatetimeFields.create(datetime=utc_now, datetime_tz_aware=now)
        obj = await testmodels.DatetimeFields.get(id=obj0.id)
        self.assertEqual(obj.datetime, utc_now)
        self.assertEqual(obj.datetime_null, None)
        self.assertLess(obj.datetime_auto - auto_now, timedelta(microseconds=20000))
        self.assertLess(obj.datetime_add - auto_now, timedelta(microseconds=20000))
        self.assertEqual(obj.datetime_tz_aware.utcoffset().total_seconds(), 27000.0)
        self.assertLess(
            obj.datetime_tz_aware - now.astimezone(timezone(timedelta(hours=7, minutes=30))),
            timedelta(microseconds=20000),
        )
        datetime_auto = obj.datetime_auto
        sleep(0.012)
        await obj.save()
        obj2 = await testmodels.DatetimeFields.get(id=obj.id)
        self.assertEqual(obj2.datetime, utc_now)
        self.assertEqual(obj2.datetime_null, None)
        self.assertEqual(obj2.datetime_auto, obj.datetime_auto)
        self.assertNotEqual(obj2.datetime_auto, datetime_auto)
        self.assertGreater(obj2.datetime_auto - auto_now, timedelta(microseconds=10000))
        self.assertLess(obj2.datetime_auto - auto_now, timedelta(seconds=1))
        self.assertEqual(obj2.datetime_add, obj.datetime_add)

    async def test_update(self):
        obj0 = await testmodels.DatetimeFields.create(datetime=datetime(2019, 9, 1, 0, 0, 0))
        await testmodels.DatetimeFields.filter(id=obj0.id).update(
            datetime=datetime(2019, 9, 1, 6, 0, 8)
        )
        obj = await testmodels.DatetimeFields.get(id=obj0.id)
        self.assertEqual(obj.datetime, datetime(2019, 9, 1, 6, 0, 8))
        self.assertEqual(obj.datetime_null, None)

    async def test_cast(self):
        now = datetime.utcnow()
        obj0 = await testmodels.DatetimeFields.create(datetime=now.isoformat())
        obj = await testmodels.DatetimeFields.get(id=obj0.id)
        self.assertEqual(obj.datetime, now)

    async def test_values(self):
        now = datetime.utcnow()
        obj0 = await testmodels.DatetimeFields.create(datetime=now)
        values = await testmodels.DatetimeFields.get(id=obj0.id).values("datetime")
        self.assertEqual(values[0]["datetime"], now)

    async def test_values_list(self):
        now = datetime.utcnow()
        obj0 = await testmodels.DatetimeFields.create(datetime=now)
        values = await testmodels.DatetimeFields.get(id=obj0.id).values_list("datetime", flat=True)
        self.assertEqual(values[0], now)

    async def test_get_utcnow(self):
        now = datetime.utcnow()
        await testmodels.DatetimeFields.create(datetime=now)
        obj = await testmodels.DatetimeFields.get(datetime=now)
        self.assertEqual(obj.datetime, now)

    async def test_get_now(self):
        now = datetime.now()
        await testmodels.DatetimeFields.create(datetime=now)
        obj = await testmodels.DatetimeFields.get(datetime=now)
        self.assertEqual(obj.datetime, now)

    async def test_count(self):
        now = datetime.now()
        obj = await testmodels.DatetimeFields.create(datetime=now)
        self.assertEqual(await testmodels.DatetimeFields.filter(datetime=obj.datetime).count(), 1)
        self.assertEqual(
            await testmodels.DatetimeFields.filter(datetime_auto=obj.datetime_auto).count(), 1
        )
        self.assertEqual(
            await testmodels.DatetimeFields.filter(datetime_add=obj.datetime_add).count(), 1
        )

    async def test_date_str(self):
        obj0 = await testmodels.DateFields.create(date="2020-08-17")
        obj1 = await testmodels.DateFields.get(date="2020-08-17")
        self.assertEqual(obj0.date, obj1.date)
        with self.assertRaises((ParseError, ValueError),):
            await testmodels.DateFields.create(date="2020-08-xx")
        await testmodels.DateFields.filter(date="2020-08-17").update(date="2020-08-18")
        obj2 = await testmodels.DateFields.get(date="2020-08-18")
        self.assertEqual(obj2.date, date(year=2020, month=8, day=18))


class TestDateFields(test.TestCase):
    async def test_empty(self):
        with self.assertRaises(IntegrityError):
            await testmodels.DateFields.create()

    async def test_create(self):
        today = date.today()
        obj0 = await testmodels.DateFields.create(date=today)
        obj = await testmodels.DateFields.get(id=obj0.id)
        self.assertEqual(obj.date, today)
        self.assertEqual(obj.date_null, None)
        await obj.save()
        obj2 = await testmodels.DateFields.get(id=obj.id)
        self.assertEqual(obj, obj2)

    async def test_cast(self):
        today = date.today()
        obj0 = await testmodels.DateFields.create(date=today.isoformat())
        obj = await testmodels.DateFields.get(id=obj0.id)
        self.assertEqual(obj.date, today)

    async def test_values(self):
        today = date.today()
        obj0 = await testmodels.DateFields.create(date=today)
        values = await testmodels.DateFields.get(id=obj0.id).values("date")
        self.assertEqual(values[0]["date"], today)

    async def test_values_list(self):
        today = date.today()
        obj0 = await testmodels.DateFields.create(date=today)
        values = await testmodels.DateFields.get(id=obj0.id).values_list("date", flat=True)
        self.assertEqual(values[0], today)

    async def test_get(self):
        today = date.today()
        await testmodels.DateFields.create(date=today)
        obj = await testmodels.DateFields.get(date=today)
        self.assertEqual(obj.date, today)

    async def test_date_str(self):
        obj0 = await testmodels.DateFields.create(date="2020-08-17")
        obj1 = await testmodels.DateFields.get(date="2020-08-17")
        self.assertEqual(obj0.date, obj1.date)
        with self.assertRaises(ValueError):
            await testmodels.DateFields.create(date="2020-08-xx")
        await testmodels.DateFields.filter(date="2020-08-17").update(date="2020-08-18")
        obj2 = await testmodels.DateFields.get(date="2020-08-18")
        self.assertEqual(obj2.date, date(year=2020, month=8, day=18))


class TestTimeDeltaFields(test.TestCase):
    async def test_empty(self):
        with self.assertRaises(IntegrityError):
            await testmodels.TimeDeltaFields.create()

    async def test_create(self):
        obj0 = await testmodels.TimeDeltaFields.create(
            timedelta=timedelta(days=35, seconds=8, microseconds=1)
        )
        obj = await testmodels.TimeDeltaFields.get(id=obj0.id)
        self.assertEqual(obj.timedelta, timedelta(days=35, seconds=8, microseconds=1))
        self.assertEqual(obj.timedelta_null, None)
        await obj.save()
        obj2 = await testmodels.TimeDeltaFields.get(id=obj.id)
        self.assertEqual(obj, obj2)

    async def test_values(self):
        obj0 = await testmodels.TimeDeltaFields.create(
            timedelta=timedelta(days=35, seconds=8, microseconds=1)
        )
        values = await testmodels.TimeDeltaFields.get(id=obj0.id).values("timedelta")
        self.assertEqual(values[0]["timedelta"], timedelta(days=35, seconds=8, microseconds=1))

    async def test_values_list(self):
        obj0 = await testmodels.TimeDeltaFields.create(
            timedelta=timedelta(days=35, seconds=8, microseconds=1)
        )
        values = await testmodels.TimeDeltaFields.get(id=obj0.id).values_list(
            "timedelta", flat=True
        )
        self.assertEqual(values[0], timedelta(days=35, seconds=8, microseconds=1))

    async def test_get(self):
        delta = timedelta(days=35, seconds=8, microseconds=1)
        await testmodels.TimeDeltaFields.create(timedelta=delta)
        obj = await testmodels.TimeDeltaFields.get(timedelta=delta)
        self.assertEqual(obj.timedelta, delta)
