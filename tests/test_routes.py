
######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
######################################################################
"""
Product API Service Test Suite

Run tests with:
    nosetests -v tests/test_routes.py
"""

import os
import logging
from decimal import Decimal
from unittest import TestCase

from service import app
from service.common import status
from service.models import db, init_db, Product
from tests.factories import ProductFactory


# Disable all but critical errors during normal test run
# logging.disable(logging.CRITICAL)

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)
BASE_URL = "/products"


######################################################################
# TEST CASES
######################################################################
# pylint: disable=too-many-public-methods
class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        """Clean up database session"""
        db.session.remove()

    ##################################################################
    # Utility function to create products
    ##################################################################
    def _create_products(self, count=1):
        """Factory method to create products in bulk"""
        products = []

        for _ in range(count):
            test_product = ProductFactory()

            response = self.client.post(
                BASE_URL,
                json=test_product.serialize(),
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )

            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)

        return products

    ##################################################################
    # INDEX AND HEALTH TESTS
    ##################################################################
    def test_index(self):
        """It should return the index page"""
        response = self.client.get("/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            b"Product Catalog Administration",
            response.data,
        )

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.get_json()
        self.assertEqual(data["message"], "OK")

    ##################################################################
    # CREATE TESTS
    ##################################################################
    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()

        logging.debug(
            "Test Product: %s",
            test_product.serialize(),
        )

        response = self.client.post(
            BASE_URL,
            json=test_product.serialize(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        # Verify Location header
        location = response.headers.get("Location")
        self.assertIsNotNone(location)

        # Verify returned product
        new_product = response.get_json()

        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(
            new_product["description"],
            test_product.description,
        )
        self.assertEqual(
            Decimal(new_product["price"]),
            test_product.price,
        )
        self.assertEqual(
            new_product["available"],
            test_product.available,
        )
        self.assertEqual(
            new_product["category"],
            test_product.category.name,
        )

        # Verify the Location URL can retrieve the product
        response = self.client.get(location)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        fetched_product = response.get_json()
        self.assertEqual(
            fetched_product["name"],
            test_product.name,
        )

    def test_create_product_with_no_name(self):
        """It should not Create a Product without a name"""
        product = self._create_products()[0]
        new_product = product.serialize()

        del new_product["name"]

        response = self.client.post(
            BASE_URL,
            json=new_product,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_product_no_content_type(self):
        """It should reject a request without Content-Type"""
        response = self.client.post(
            BASE_URL,
            data="bad data",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    def test_create_product_wrong_content_type(self):
        """It should reject an incorrect Content-Type"""
        response = self.client.post(
            BASE_URL,
            data="{}",
            content_type="plain/text",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    ##################################################################
    # READ TESTS
    ##################################################################
    def test_read_a_product(self):
        """It should Read a single Product"""
        product = self._create_products(1)[0]

        response = self.client.get(
            f"{BASE_URL}/{product.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.get_json()
        self.assertEqual(data["id"], product.id)
        self.assertEqual(data["name"], product.name)
        self.assertEqual(
            data["description"],
            product.description,
        )

    def test_read_product_not_found(self):
        """It should return 404 when a product does not exist"""
        response = self.client.get(
            f"{BASE_URL}/99999"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    ##################################################################
    # UPDATE TESTS
    ##################################################################
    def test_update_product(self):
        """It should Update an existing Product"""
        product = self._create_products(1)[0]

        updated_data = product.serialize()
        updated_data["name"] = "UpdatedProduct"

        response = self.client.put(
            f"{BASE_URL}/{product.id}",
            json=updated_data,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.get_json()
        self.assertEqual(data["name"], "UpdatedProduct")

        # Verify the change persisted
        response = self.client.get(
            f"{BASE_URL}/{product.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.get_json()["name"],
            "UpdatedProduct",
        )

    def test_update_product_not_found(self):
        """It should return 404 when updating a missing product"""
        product = ProductFactory()

        response = self.client.put(
            f"{BASE_URL}/99999",
            json=product.serialize(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    ##################################################################
    # DELETE TESTS
    ##################################################################
    def test_delete_product(self):
        """It should Delete a Product"""
        product = self._create_products(1)[0]

        response = self.client.delete(
            f"{BASE_URL}/{product.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        # Verify it no longer exists
        response = self.client.get(
            f"{BASE_URL}/{product.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_delete_product_not_found(self):
        """It should return 404 when deleting a missing product"""
        response = self.client.delete(
            f"{BASE_URL}/99999"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    ##################################################################
    # LIST TESTS
    ##################################################################
    def test_list_all_products(self):
        """It should List all Products"""
        self._create_products(3)

        response = self.client.get(BASE_URL)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.get_json()), 3)

    ##################################################################
    # SEARCH TESTS
    ##################################################################
    def test_search_products_by_name(self):
        """It should Search Products by name"""
        product = self._create_products(1)[0]

        response = self.client.get(
            BASE_URL,
            query_string={"name": product.name},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.get_json()
        self.assertTrue(
            any(item["name"] == product.name for item in data)
        )

    def test_search_products_by_category(self):
        """It should Search Products by category"""
        product = self._create_products(1)[0]

        response = self.client.get(
            BASE_URL,
            query_string={
                "category": product.category.name,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.get_json()
        self.assertTrue(
            all(
                item["category"] == product.category.name
                for item in data
            )
        )

    def test_search_products_by_availability(self):
        """It should Search Products by availability"""
        product = self._create_products(1)[0]

        response = self.client.get(
            BASE_URL,
            query_string={
                "available": str(product.available).lower(),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.get_json()
        self.assertTrue(
            all(
                item["available"] == product.available
                for item in data
            )
        )

    ##################################################################
    # UTILITY FUNCTIONS
    ##################################################################
    def get_product_count(self):
        """Return the current number of products"""
        response = self.client.get(BASE_URL)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.get_json()
        return len(data)
