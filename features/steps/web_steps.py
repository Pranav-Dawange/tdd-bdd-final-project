
######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
######################################################################

"""
Web Steps

Step definitions for browser interactions with Selenium.
"""

import logging

from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "product_"


@when('I visit the "Home Page"')
def step_impl(context):
    """Visit the application home page."""
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the browser page title."""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    """Verify that text is absent from the page."""
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    """Set a text input field."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    """Select an option from a dropdown."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    """Verify the selected dropdown option."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    """Verify that an input field is empty."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# Copy and paste simulation
##################################################################

@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    """Copy a field value into a simulated clipboard."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")

    element = WebDriverWait(
        context.driver, context.wait_seconds
    ).until(
        expected_conditions.presence_of_element_located(
            (By.ID, element_id)
        )
    )

    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    """Paste the simulated clipboard value into a field."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")

    element = WebDriverWait(
        context.driver, context.wait_seconds
    ).until(
        expected_conditions.presence_of_element_located(
            (By.ID, element_id)
        )
    )

    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# Button and message steps
##################################################################

@when('I press the "{button_name}" button')
def step_impl(context, button_name):
    """Click a button using its ID."""
    button_id = button_name.lower().replace(" ", "-") + "-btn"

    button = WebDriverWait(
        context.driver, context.wait_seconds
    ).until(
        expected_conditions.element_to_be_clickable(
            (By.ID, button_id)
        )
    )

    button.click()


@then('I should see the message "{message}"')
def step_impl(context, message):
    """Verify that a message is displayed on the page."""
    element = WebDriverWait(
        context.driver, context.wait_seconds
    ).until(
        expected_conditions.text_to_be_present_in_element(
            (By.TAG_NAME, "body"),
            message
        )
    )

    assert element


##################################################################
# Field verification steps
##################################################################

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    """Verify the value of a text input field."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")

    found = WebDriverWait(
        context.driver, context.wait_seconds
    ).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )

    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    """Change a text input field."""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")

    element = WebDriverWait(
        context.driver, context.wait_seconds
    ).until(
        expected_conditions.presence_of_element_located(
            (By.ID, element_id)
        )
    )

    element.clear()
    element.send_keys(text_string)
