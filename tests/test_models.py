
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m
"""

import os
import logging
import unittest
from decimal import Decimal

from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
# PRODUCT MODEL TEST CASES
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    # CREATE TESTS
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertIsNotNone(product)
        self.assertIsNone(product.id)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        self.assertEqual(Product.all(), [])

        product = ProductFactory()
        product.id = None
        product.create()

        self.assertIsNotNone(product.id)

        products = Product.all()
        self.assertEqual(len(products), 1)

        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    ######################################################################
    # READ TEST
    ######################################################################

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.create()

        found = Product.find(product.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)

    ######################################################################
    # UPDATE TEST
    ######################################################################

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.create()

        product.name = "Updated Product"
        product.description = "Updated description"
        product.update()

        found = Product.find(product.id)

        self.assertEqual(found.name, "Updated Product")
        self.assertEqual(found.description, "Updated description")

    ######################################################################
    # DELETE TEST
    ######################################################################

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        product_id = product.id

        product.delete()

        self.assertIsNone(Product.find(product_id))

    ######################################################################
    # LIST ALL TEST
    ######################################################################

    def test_list_all_products(self):
        """It should List All Products"""
        products = ProductFactory.create_batch(5)

        for product in products:
            product.create()

        found = Product.all()
        self.assertEqual(len(found), 5)

    ######################################################################
    # FIND BY NAME TEST
    ######################################################################

    def test_find_product_by_name(self):
        """It should Find Products by Name"""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        product.create()

        found = Product.find_by_name("Fedora").all()

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].name, "Fedora")

    ######################################################################
    # FIND BY CATEGORY TEST
    ######################################################################

    def test_find_products_by_category(self):
        """It should Find Products by Category"""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        product.create()

        found = Product.find_by_category(Category.CLOTHS).all()

        self.assertGreaterEqual(len(found), 1)
        self.assertTrue(
            all(item.category == Category.CLOTHS for item in found)
        )

    ######################################################################
    # FIND BY AVAILABILITY TEST
    ######################################################################

    def test_find_products_by_availability(self):
        """It should Find Products by Availability"""
        product = Product(
            name="Available Product",
            description="An available product",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        product.create()

        found = Product.find_by_availability(True).all()

        self.assertGreaterEqual(len(found), 1)
        self.assertTrue(all(item.available for item in found))
