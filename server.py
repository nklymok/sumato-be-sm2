from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator, ConfigDict
from supermemo2 import first_review, review

app = FastAPI(openapi_prefix="/sm2", docs_url="/docs")


class SM2Request(BaseModel):
    correct: bool
    easiness: Optional[float] = None
    interval: Optional[int] = None
    repetitions: Optional[int] = None

    @model_validator(mode="before")
    def validate_review_fields(cls, values: dict) -> dict:
        eas, iv, rep = (
            values.get("easiness"),
            values.get("interval"),
            values.get("repetitions"),
        )
        all_none = eas is None and iv is None and rep is None
        all_present = eas is not None and iv is not None and rep is not None

        if not (all_none or all_present):
            raise ValueError(
                "`easiness`, `interval` and `repetitions` must be provided together or omitted together"
            )
        return values


class SM2Response(BaseModel):
    ease_factor: float
    interval: int
    repetitions: int
    review_datetime: datetime = Field(
        ..., description="UTC timestamp in ISO-8601, e.g. '2025-05-11T12:38:19Z'"
    )
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        }
    )


@app.post("/", response_model=SM2Response)
def process_sm2(payload: SM2Request):
    # Determine whether to run first_review or review()
    if payload.easiness is not None:
        result = review(
            3 if payload.correct else 0,
            payload.easiness,
            payload.interval,
            payload.repetitions
        )
    else:
        result = first_review(3 if payload.correct else 0)

    return SM2Response(
        ease_factor=result['easiness'],
        interval=result['interval'],
        repetitions=result['repetitions'],
        review_datetime=result['review_datetime']
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8081)
