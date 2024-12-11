from datetime import datetime
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pytonconnect import TonConnect

from requests import CheckProofRequest

# from tonutils.client import TonapiClient
# from tonutils

TON_API_KEY = "AF2YUOUVVZASO7AAAAAHSDOPWPGOF4LOYLDLZDUF7INN3A4IHORBAZAT3N2FHAAOHEGWCLQ"
# api = TonapiClient(api_key=TON_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# TODO: move to main
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://589a-2a12-5940-76ab-00-2.ngrok-free.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*", "ngrok-skip-browser-warning"],
)

# TON Connect instance
connector = TonConnect(
    manifest_url='https://raw.githubusercontent.com/daria021/dummy/refs/heads/main/tonconnect-manifest.json',
)

# Store active connection status
connections = {}


# Utility to generate payload
def generate_payload(ttl: int) -> str:
    payload = bytearray(uuid4().bytes)
    ts = int(datetime.now().timestamp()) + ttl
    payload.extend(ts.to_bytes(8, 'big'))
    return payload.hex()


# Utility to verify payload
def verify_payload_and_signature(
        request: CheckProofRequest
) -> bool:
    """
    Verify the payload structure, expiration, and signature validity.

    Args:
        signed_payload (str): Payload signed by the user's wallet.
        payload_hex (str): The original payload in hexadecimal format.
        wallet_address (str): The user's wallet address.

    Returns:
        bool: True if the payload and signature are valid, False otherwise.
    """
    return True


class DisconnectRequest(BaseModel):
    address: str


# Generate a payload for connection
@app.get("/auth/payload")
async def generate_proof_payload(
        request: Request,
):
    try:
        proof_payload = generate_payload(600)
        print(proof_payload, request.method)
        return {"payload": proof_payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


COOKIE_KEY = 'widepiper-token'


# Verify connection payload
@app.post("/auth/verify_payload")
async def verify_proof_payload(
        request: CheckProofRequest,
        response: Response,
):
    try:
        if verify_payload_and_signature(request):
            response.set_cookie(
                key=COOKIE_KEY,
                value="Bearer abc",
                httponly=True,
                secure=True,
                # samesite='none',
            )
            return
        else:
            raise HTTPException(status_code=401, detail="Proof check failed. Are you a villain?")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'lol: {str(e)}')


@app.post('/auth/logout')
async def logout(
        response: Response,
):
    response.delete_cookie(COOKIE_KEY)
    return


@app.post('/auth/refresh')
async def refresh(
        response: Response,
        token: str = Cookie(alias='widepiper-token', default=None),
):
    if not token:
        raise HTTPException(status_code=401, detail='Token not provided')
    if token == 'Bearer abc':
        response.set_cookie(COOKIE_KEY, 'Bearer abc')
    else:
        raise HTTPException(status_code=403, detail='Wrong token, fuck you!')


class UserInfoResponse(BaseModel):
    balances: dict[
        Annotated[str, 'Token name'],
        Annotated[float, 'User balance'],
    ]
    total_balance: Annotated[float, 'Total user balance in USDT equivalent']
    at_risk: Annotated[float, 'Total user bets amount']


@app.get('/user')
async def get_user_info(
        token: str = Cookie(alias='widepiper-token', default=None),
) -> UserInfoResponse:
    if not token:
        print('token is none')
        raise HTTPException(status_code=401, detail='Token not provided')
    if token == 'Bearer abc':
        return UserInfoResponse(
            balances={
                'TON': 12.1,
                'USDT': 132.4,
            },
            total_balance=200.5,
            at_risk=1323.7,
        )
    else:
        raise HTTPException(status_code=403, detail='Wrong token, fuck you!')


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
