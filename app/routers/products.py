from fastapi import APIRouter

router = APIRouter()


@router.get("/product/{uid}")
async def get_product(uid: str):
    pass


@router.post("/product/")
async def add_product():
    pass


@router.delete("/product/{uid}")
async def delete_product(uid: str):
    pass
