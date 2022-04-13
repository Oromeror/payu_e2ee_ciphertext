from fastapi import APIRouter, HTTPException, Header, Depends
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import requests

import jose
from time import time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app_payu_hub_e2ee_card = APIRouter()

@app_payu_hub_e2ee_card.get(
    path='/ciphertext/{account_id}/keys/{key_name}/versions/{key_version}',
    status_code=HTTP_200_OK,
    tags=['Generate ciphertext'],
    summary="Create a card ciphertext"
)

async def create_JWE(
    account_id: str, 
    key_name: str,
    key_version: str,
    api_version: Optional[str] = Header(None),
    x_payments_os_env: Optional[str] = Header(None),
    token: str = Depends(oauth2_scheme)
    ):

    '''
    Retrieves a public key PEM for the specified key name and version from the PayU Hub Management API.
    https://developers.paymentsos.com/docs/apis/management/1.1.0/#operation/retrieve-a-key-pem-file
    '''

    url = f"https://api.paymentsos.com/accounts/{account_id}/keys/{key_name}/versions/{key_version}/download?type=public_key"

    headers = {
        "api-version": api_version,
        "x-payments-os-env": x_payments_os_env,
        'Authorization': 'Bearer ' + token
    }

    get_response = requests.get(url, headers = headers)

    if get_response.status_code != 200:
        raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=get_response.content.decode('utf-8')
                )
    else:
        
        PEM = get_response.content.decode('utf-8')
        print(PEM) # to debug

        '''
        JOSE framework use of JWE
        PayU Hub: https://developers.paymentsos.com/docs/security/e2ee.html
        Javascript Object Signing and Encryption (JOSE) framework: https://jose.readthedocs.io/en/latest/#f1
        '''

        claims = {
        'iss': 'http://www.example.com',
        'exp': int(time()) + 600,
        'sub': 42
        }

        # encrypt claims using the public key
        pub_jwk = {'k': PEM}

        jwe = jose.encrypt(claims, pub_jwk)

        response = jsonable_encoder(jwe)

        return HTTPException(
            status_code=HTTP_200_OK,
            detail=JSONResponse(content=response)
        );