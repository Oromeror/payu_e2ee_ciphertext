#from os import path
#from database.mysql import execute_query
from fastapi import APIRouter, HTTPException, Request, Header, Depends
#from interface.card import Card
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

async def create_ciphertext(
    account_id: str, 
    key_name: str,
    key_version: str,
    api_version: Optional[str] = Header(None),
    x_payments_os_env: Optional[str] = Header(None),
    token: str = Depends(oauth2_scheme)
    ):

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

        PEM_file = get_response.content.decode('utf-8')
    
        claims = {
        'iss': 'http://www.example.com',
        'exp': int(time()) + 600,
        'sub': 42,
        }

        # encrypt claims using the public key
        pub_jwk = {'k': PEM_file}
        jwe = jose.encrypt(claims, pub_jwk)
        response = jsonable_encoder(jwe)

        return HTTPException(
            status_code=HTTP_200_OK,
            detail=JSONResponse(content=response)
        )

    """
    //Documentation: https://jose.readthedocs.io/en/latest/#f1

    import jose
    from time import time
    from Crypto.PublicKey import RSA

    # key for demonstration purposes
    key = RSA.generate(2048)

    claims = {
        'iss': 'http://www.example.com',
        'exp': int(time()) + 3600,
        'sub': 42,
    }

    # encrypt claims using the public key
    pub_jwk = {'k': key.publickey().exportKey('PEM')}

    jwe = jose.encrypt(claims, pub_jwk)
    # JWE(header='eyJhbGciOiAiUlNBLU9BRVAiLCAiZW5jIjogIkExMjhDQkMtSFMyNTYifQ',
    # cek='SsLgP2bNKYDYGzHvLYY7rsVEBHSms6_jW-WfglHqD9giJhWwrOwqLZOaoOycsf_EBJCkHq9-vbxRb7WiNdy_C9J0_RnRRBGII6z_G4bVb18bkbJMeZMV6vpUut_iuRWoct_weg_VZ3iR2xMbl-yE8Hnc63pAGJcIwngfZ3sMX8rBeni_koxCc88LhioP8zRQxNkoNpvw-kTCz0xv6SU_zL8p79_-_2zilVyMt76Pc7WV46iI3EWIvP6SG04sguaTzrDXCLp6ykLGaXB7NRFJ5PJ9Lmh5yinAJzCdWQ-4XKKkNPorSiVmRiRSQ4z0S2eo2LtvqJhXCrghKpBNgbtnJQ',
    # iv='Awelp3ryBVpdFhRckQ-KKw',
    # ciphertext='1MyZ-3nky1EFO4UgTB-9C2EHpYh1Z-ij0RbiuuMez70nIH7uqL9hlhskutO0oPjqdpmNc9glSmO9pheMH2DVag',
    # tag='Xccck85XZMvG-fAJ6oDnAw')

    # issue the compact serialized version to the clients. this is what will be
    # transported along with requests to target systems.

    jwt = jose.serialize_compact(jwe)
    # 'eyJhbGciOiAiUlNBLU9BRVAiLCAiZW5jIjogIkExMjhDQkMtSFMyNTYifQ.SsLgP2bNKYDYGzHvLYY7rsVEBHSms6_jW-WfglHqD9giJhWwrOwqLZOaoOycsf_EBJCkHq9-vbxRb7WiNdy_C9J0_RnRRBGII6z_G4bVb18bkbJMeZMV6vpUut_iuRWoct_weg_VZ3iR2xMbl-yE8Hnc63pAGJcIwngfZ3sMX8rBeni_koxCc88LhioP8zRQxNkoNpvw-kTCz0xv6SU_zL8p79_-_2zilVyMt76Pc7WV46iI3EWIvP6SG04sguaTzrDXCLp6ykLGaXB7NRFJ5PJ9Lmh5yinAJzCdWQ-4XKKkNPorSiVmRiRSQ4z0S2eo2LtvqJhXCrghKpBNgbtnJQ.Awelp3ryBVpdFhRckQ-KKw.1MyZ-3nky1EFO4UgTB-9C2EHpYh1Z-ij0RbiuuMez70nIH7uqL9hlhskutO0oPjqdpmNc9glSmO9pheMH2DVag.Xccck85XZMvG-fAJ6oDnAw'

    # decrypt on the other end using the private key
    priv_jwk = {'k': key.exportKey('PEM')}

    jwt = jose.decrypt(jose.deserialize_compact(jwt), priv_jwk)
    # JWT(header={u'alg': u'RSA-OAEP', u'enc': u'A128CBC-HS256'},
    # claims={u'iss': u'http://www.example.com', u'sub': 42, u'exp': 1395606273})
    """