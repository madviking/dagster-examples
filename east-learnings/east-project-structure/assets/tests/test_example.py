import pytest
from dagster import build_op_context
from app.assets.database2.md_companies import md_nordic_companies_last_month
from app.resources.mysql import MySQLResource, production_resource

def test_md_nordic_companies_last_month():
    # Mock the resources
    resources = {
        "production_resource": production_resource(),
    }

    # Build the context
    context = build_op_context(resources=resources)

    # Call the asset function
    result = md_nordic_companies_last_month(context)

    # Check that the result is a list
    assert isinstance(result, list), "Result should be a list"
    assert len(result) > 0, "Result should not be empty"
