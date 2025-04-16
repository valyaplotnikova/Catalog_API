from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/")
async def get_catalog():
    pass


@router.get("/catalog/filter/")
async def get_filters():
    pass

