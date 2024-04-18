from fastapi import APIRouter, HTTPException, status, Header, Depends
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from datetime import datetime, timedelta
from jwcrypto import jwk, jwe
from time import time
import requests
import json

# Request Model definition
class CardRequestModel(BaseModel):
    credit_card_number: str = Field(
        ..., 
        min_length=12, 
        max_length=19, 
        description="Credit card number"
    )
    cvv: str = Field(
        ...,
        min_length=3, 
        max_length=4, 
        description="CVV code"
    )

app_payu_hub_e2ee_card = APIRouter()

@app_payu_hub_e2ee_card.post(
    path="/e2ee/{account_id}/keys/{key_name}/versions/{key_version}",
    status_code=status.HTTP_200_OK,
    tags=["Generate card ciphertext"],
    summary="Create a card ciphertext",
)
def generate_encrypted_card(
    req: CardRequestModel, 
    account_id: str, 
    key_name: str, 
    key_version: str
    ):
    """
    Returns the ciphertext generated with the private function encrypt_card_data()
    to be used in the Charge or the Authorization creation
    """
    try:
        # Get session token from PaymentsOS
        session_token = _get_session_token()

        # Retrieve key from PaymentsOS
        public_key = _retrieve_key(
                session_token, 
                account_id, 
                key_name, 
                key_version
            )

        # Retrieve PEM file from PaymentsOS
        public_key_pem = _download_key_pem(
                session_token, 
                account_id, 
                key_name, 
                key_version, 
                type='public_key'
            )
    
        # Encrypt card data
        encrypted_card_data = _encrypt_card_data(
                req.dict(),
                public_key, 
                public_key_pem, 
            )

        # Return JSON response
        return JSONResponse(
            content={"status": 200, "data": encrypted_card_data},
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def _get_session_token():
    """
    Retrieve a PaymentsOs session token
    docs: https://developers.paymentsos.com/docs/apis/management/1.1.0/#tag/Sessions
    """
    url = "https://api.paymentsos.com/sessions"
    body = {
        "email": "",  # PaymentsOS Admin Email
        "password": "",  # PaymentsOS Admin Password
    }

    # Send a POST request to the URL
    response = requests.post(url, json=body)

    # Check if the request was successful
    if response.status_code == 201:
        # Return the session token from the response data
        session_token = response.json().get("session_token")
        return session_token
    else:
        # Handle error cases (e.g. print an error message)
        print(
            f"Failed to retrieve PayU Hub session token. Status code: {response.status_code}; response was: {response.text}"
        )
        return None

def _retrieve_key(session_token: str, account_id: str, key_name: str, key_version: str) -> dict:
    """
    Retrieve a PaymentsOs Key by Version
    docs: https://developers.paymentsos.com/docs/apis/management/1.1.0/#operation/retrieve-a-key-by-version
    """

    # Define the URL based on the request parameters
    url = f"https://api.paymentsos.com/accounts/{account_id}/keys/{key_name}/versions/{key_version}"

    # Define the request headers
    headers = {
        "api-version": "1.3.0",
        "x-payments-os-env": "test",
        "Authorization": f"Bearer {session_token}",
    }

    try:
        # Send a GET request to the URL with the headers
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Return the data from the response
            return response.json()
        else:
            # Handle error cases
            raise Exception(
                f"Retrieve key request failed with status code: {response.status_code}; response was: {response.text}"
            )

    except requests.RequestException as e:
        print(f"Request error: {e}")
        raise e

def _download_key_pem(session_token: str, account_id: str, key_name: str, key_version: str, type: str) -> dict:
    """
    Download a PaymentsOs Key PEM File by Version
    docs: https://developers.paymentsos.com/docs/apis/management/1.1.0/#operation/retrieve-a-key-by-version
    """

    # Define the URL based on the request parameters
    url = f"https://api.paymentsos.com/accounts/{account_id}/keys/{key_name}/versions/{key_version}/download?type={type}"

    # Define the request headers
    headers = {
        "api-version": "1.3.0",
        "x-payments-os-env": "test",
        "Authorization": f"Bearer {session_token}",
    }

    try:
        # Send a GET request to the URL with the headers
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Return the data from the response
            return response.text
        else:
            # Handle error cases
            raise Exception(
                f"Retrieve key PEM request failed with status code: {response.status_code}; response was: {response.text}"
            )

    except requests.RequestException as e:
        print(f"Request error: {e}")
        raise e

def _encrypt_card_data(card: dict, public_key: dict, public_key_pem: str) -> str:
    """
    Encrypts card data
    docs: https://developers.paymentsos.com/docs/security/e2ee.html
    Using jwcrypto library
    """

    # payload
    plaintext = json.dumps(card).encode('utf-8')

    # Obtain protected headers from public key
    protected_headers = public_key.get("protected_headers", {})
    kid = protected_headers.get("kid", None)
    enc = protected_headers.get("enc", None)

    # Create JWK object from PEM-encoded public key
    try:
        rsa_public_key = jwk.JWK.from_pem(public_key_pem.encode('utf-8'))
    except Exception as e:
        print(f"Error creating JWK from PEM: {e}")
        return None

    # Set expiration time for the token
    token_ttl_min = 10
    created_date = datetime.utcnow()
    expired_date = created_date + timedelta(minutes=token_ttl_min)

    # Protected headers with "iat", "exp" and "alg"
    protected = {
        "kid": kid,
        "enc": enc,
        "iat": int(created_date.timestamp()),  # Issued at time
        "exp": int(expired_date.timestamp()),  # Expiration time
        "alg": "RSA-OAEP-256",
    }

    # Create JWE token
    jwe_token = jwe.JWE(
            plaintext=plaintext, 
            recipient=rsa_public_key, 
            protected=protected
        )

    # Serializes jwe_token
    jwe_compact = jwe_token.serialize(True)

    # Returd encrypted card data
    return {
        "jwe_compact": jwe_compact
    }