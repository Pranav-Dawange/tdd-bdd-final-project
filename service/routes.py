
######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
######################################################################

"""
Product Store Service with UI
"""

from flask import jsonify, request, abort, url_for
from service.models import Product, Category, DataValidationError
from service.common import status
from . import app


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# HOME PAGE
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# UTILITY FUNCTIONS
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if request.headers.get("Content-Type") != content_type:
        app.logger.error("Invalid or missing Content-Type")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )


######################################################################
# CREATE A NEW PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """Creates a Product"""
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json(silent=True)
    if not data:
        abort(status.HTTP_400_BAD_REQUEST, "Invalid or missing JSON data")

    product = Product()
    try:
        product.deserialize(data)
        product.create()
    except (DataValidationError, ValueError) as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))

    message = product.serialize()
    location_url = url_for(
        "get_product", product_id=product.id, _external=True
    )

    return (
        jsonify(message),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# LIST ALL PRODUCTS AND SEARCH PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns all products or filters by name, category, or availability"""
    app.logger.info("Request to list Products...")

    products = Product.all()

    # Search by name
    name = request.args.get("name")
    if name:
        products = Product.find_by_name(name).all()

    # Search by category
    category = request.args.get("category")
    if category:
        try:
            category_value = Category[category.upper()]
        except KeyError:
            abort(status.HTTP_400_BAD_REQUEST, "Invalid product category")
        products = Product.find_by_category(category_value).all()

    # Search by availability
    available = request.args.get("available")
    if available is not None:
        available_value = available.lower()
        if available_value not in ("true", "false"):
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Availability must be true or false",
            )
        products = Product.find_by_availability(
            available_value == "true"
        ).all()

    return jsonify([product.serialize() for product in products]), status.HTTP_200_OK


######################################################################
# READ A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Reads a single Product"""
    app.logger.info("Request to Read Product id=%s", product_id)

    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, "Product not found")

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Updates an existing Product"""
    app.logger.info("Request to Update Product id=%s", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, "Product not found")

    data = request.get_json(silent=True)
    if not data:
        abort(status.HTTP_400_BAD_REQUEST, "Invalid or missing JSON data")

    try:
        product.deserialize(data)
        product.id = product_id
        product.update()
    except (DataValidationError, ValueError) as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Deletes a Product"""
    app.logger.info("Request to Delete Product id=%s", product_id)

    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, "Product not found")

    product.delete()
    return "", status.HTTP_204_NO_CONTENT
