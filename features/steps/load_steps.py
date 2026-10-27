
######################################################################
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
######################################################################

"""
Product Steps

Steps file for products.feature
"""

import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("the following products")
def step_impl(context):
    """Delete all existing products and load new ones."""
    rest_endpoint = f"{context.base_url}/products"

    # List all existing products
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK, (
        f"Could not list products: {context.resp.text}"
    )

    # Delete existing products
    for product in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{product['id']}"
        )
        assert context.resp.status_code == HTTP_204_NO_CONTENT, (
            f"Could not delete product {product['id']}: "
            f"{context.resp.text}"
        )

    # Create products from the feature table
    for row in context.table:
        product = {
            "name": row["name"],
            "description": row["description"],
            "price": float(row["price"]),
            "available": row["available"].strip().lower() == "true",
            "category": row["category"].strip().upper(),
        }

        context.resp = requests.post(
            rest_endpoint,
            json=product,
        )

        assert context.resp.status_code == HTTP_201_CREATED, (
            f"Could not create product {product['name']}: "
            f"HTTP {context.resp.status_code} - {context.resp.text}"
        )
