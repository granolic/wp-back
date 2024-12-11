import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from dependencies.services.user import get_user_service
from domain.metaholder.responses import UserInfoResponse, BalanceResponse, UserBetsResponse, BetResponse, \
    UserHistoryResponse
from services.exceptions import NotFoundException

router = APIRouter(
    prefix='/user',

)

logger = logging.getLogger(__name__)


@router.get('')
async def get_user_info(
        request: Request,
) -> UserInfoResponse:
    user_id = request.scope.get('x_user_id', None)

    assert user_id

    users = get_user_service()

    try:
        user = await users.get_user(user_id)
        user_info = UserInfoResponse(
            user_id=user.id,
            balances=[
                BalanceResponse(
                    balance=x.balance,
                    token_type=x.token_type,
                ) for x in user.balances
            ],
        )
        return user_info
    except NotFoundException:
        logger.error(f"No user with ID {user_id}", exc_info=True)
        raise HTTPException(
            status_code=404,
            detail=f"No user with ID {user_id}",
        )


@router.get('/bets')
async def get_users_bets(tg_id: int) -> UserBetsResponse:
    users = get_user_service()

    try:
        user = await users.get_user_by_tg_id(tg_id=tg_id)
        user_bets = UserBetsResponse(
            user_id=user.id,
            bets=[
                BetResponse(
                    amount=x.amount,
                    vector=x.vector,
                    pair_name=x.pair.name,
                    created_at=x.created_at,
                ) for x in user.bets
            ],
        )
        return user_bets
    except NotFoundException:
        logger.error(f"No user with TG ID {tg_id}", exc_info=True)
        raise HTTPException(
            status_code=404,
            detail=f"No user with TG ID {tg_id}",
        )


@router.get('/history')
async def get_user_history(tg_id: int) -> UserHistoryResponse:
    ...
