import json
from http import HTTPStatus
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import Response


router = APIRouter()


class StrokeData(BaseModel):
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None


"""
Becuase of the router, every endpoint in this file is prefixed with /events/
"""


@router.post("/", dependencies=[])
def handle_event(
    data: StrokeData,
) -> Response:
    print(data)

    # This is where you implement the AI logic to handle the event

    # Return acceptance response
    return Response(
        content=json.dumps({"message": "Data received!"}),
        status_code=HTTPStatus.ACCEPTED,
    )