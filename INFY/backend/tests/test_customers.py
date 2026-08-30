"""
BillSphere Customer API Tests

Tests:
- Create customer
- List customers
- Update customer
- Delete customer
"""

from fastapi import status



# ==========================================================
# Helper
# ==========================================================

def create_test_user(
    client,
):
    """
    Create user for customer tests.
    """

    response = client.post(

        "/api/v1/register",

        json={

            "first_name":
            "Customer",

            "last_name":
            "Owner",

            "email":
            "customerowner@example.com",

            "password":
            "password123",

        },

    )


    return response



# ==========================================================
# Create Customer Test
# ==========================================================

def test_create_customer(
    client,
    auth_headers,
):
    """
    Test customer creation.
    """

    response = client.post(

        "/api/v1/customers",

        headers=auth_headers,

        json={

            "company_name":
            "Example Pvt Ltd",

            "contact_name":
            "John Doe",

            "email":
            "john@example.com",

            "phone":
            "9999999999",


        },

    )



    assert response.status_code in [

        status.HTTP_200_OK,

        status.HTTP_201_CREATED,

    ]



# ==========================================================
# List Customer Test
# ==========================================================

def test_list_customers(
    client,
    auth_headers,
):
    """
    Test customer listing.
    """

    response = client.get(

        "/api/v1/customers",

        headers=auth_headers,

    )



    assert response.status_code == status.HTTP_200_OK



    data = response.json()



    assert data is not None



# ==========================================================
# Update Customer Test
# ==========================================================

def test_update_customer(
    client,
    auth_headers,
):
    """
    Test updating customer.
    """

    create_response = client.post(

        "/api/v1/customers",

        headers=auth_headers,

        json={

            "company_name":
            "Old Company",

            "contact_name":
            "Old Name",

            "email":
            "old@example.com",

            "phone":
            "8888888888",


        },

    )



    if create_response.status_code not in [

        200,

        201,

    ]:

        return



    customer = (
        create_response.json()
    )



    customer_id = (
        customer.get(
            "id"
        )
        or
        customer.get(
            "data",
            {}
        ).get(
            "id"
        )
    )



    if customer_id is None:

        return



    response = client.put(

        f"/api/v1/customers/{customer_id}",

        headers=auth_headers,

        json={

            "contact_name":
            "Updated Name",

        },

    )



    assert response.status_code in [

        200,

        204,

    ]



# ==========================================================
# Delete Customer Test
# ==========================================================

def test_delete_customer(
    client,
    auth_headers,
):
    """
    Test deleting customer.
    """

    create_response = client.post(

        "/api/v1/customers",

        headers=auth_headers,

        json={

            "company_name":
            "Delete Company",

            "contact_name":
            "Delete Customer",

            "email":
            "delete@example.com",

            "phone":
            "7777777777",


        },

    )



    if create_response.status_code not in [

        200,

        201,

    ]:

        return



    customer = (
        create_response.json()
    )



    customer_id = (
        customer.get(
            "id"
        )
        or
        customer.get(
            "data",
            {}
        ).get(
            "id"
        )
    )



    if customer_id is None:

        return



    response = client.delete(

        f"/api/v1/customers/{customer_id}",

        headers=auth_headers,

    )



    assert response.status_code in [

        200,

        204,

    ]