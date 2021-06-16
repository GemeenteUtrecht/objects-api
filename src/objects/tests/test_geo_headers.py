from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from objects.accounts.constants import PermissionModes
from objects.accounts.tests.factories import ObjectPermissionFactory
from objects.core.tests.factories import ObjectFactory
from objects.utils.test import TokenAuthMixin

from .constants import GEO_READ_KWARGS, POLYGON_AMSTERDAM_CENTRUM

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/a6c109"


class GeoHeaderTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        ObjectPermissionFactory(
            object_type=OBJECT_TYPE,
            mode=PermissionModes.read_and_write,
            users=[cls.user],
        )

    def assertResponseHasGeoHeaders(self, response):
        self.assertTrue("Content-Crs" in response)
        self.assertEqual(response["Content-Crs"], "EPSG:4326")

    def test_get_without_geo_headers(self):
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseHasGeoHeaders(response)

    def test_get_with_geo_headers(self):
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url, **GEO_READ_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseHasGeoHeaders(response)

    def test_get_with_incorrect_get_headers(self):
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url, HTTP_ACCEPT_CRS="EPSG:3857")

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_without_geo_headers(self):
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 30},
                "startAt": "2020-01-01",
            },
        }
        url = reverse("object-list")

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_412_PRECONDITION_FAILED)

    def test_update_without_geo_headers(self):
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 30},
                "startAt": "2020-01-01",
            },
        }

        for method in ("put", "patch"):
            with self.subTest(method=method):
                do_request = getattr(self.client, method)

                response = do_request(url, data)

                self.assertEqual(
                    response.status_code, status.HTTP_412_PRECONDITION_FAILED
                )

    def test_delete_without_geo_headers(self):
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_without_geo_headers(self):
        url = reverse("object-search")

        response = self.client.post(
            url,
            {
                "geometry": {
                    "within": {
                        "type": "Polygon",
                        "coordinates": [POLYGON_AMSTERDAM_CENTRUM],
                    }
                }
            },
        )

        self.assertEqual(response.status_code, status.HTTP_412_PRECONDITION_FAILED)
