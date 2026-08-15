from fastapi import APIRouter, Request

router = APIRouter()


@router.api_route(
    "/ping",
    methods=["GET", "HEAD"],
    tags=["Health Check"],
    description="检查服务可用性",
    response_description="pong",
)
def ping(request: Request) -> str:
    return "pong"
