import random
from datetime import date, timedelta

import factory
from django.contrib.gis.geos import Point

from ..models import Object, ObjectRecord
from factory.fuzzy import BaseFuzzyAttribute


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0),
                     random.uniform(-90.0, 90.0))


class ObjectDataFactory(factory.DictFactory):
    some_field = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    city = factory.Faker("city")
    description = factory.Faker("sentence")
    diameter = factory.LazyAttribute(lambda x: random.randrange(1, 10_000))


class ObjectFactory(factory.django.DjangoModelFactory):
    object_type = factory.Faker("url")

    class Meta:
        model = Object


class ObjectRecordFactory(factory.django.DjangoModelFactory):
    object = factory.SubFactory(ObjectFactory)
    version = factory.Sequence(lambda n: n)
    data = factory.SubFactory(ObjectDataFactory)
    start_at = factory.fuzzy.FuzzyDate(
        start_date=date.today() - timedelta(days=365),
        end_date=date.today(),
    )
    geometry = FuzzyPoint()

    class Meta:
        model = ObjectRecord
