from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from crud.products_crud import ProductCRUD
from database.database import db_helper
from utils import parse_query_params

router = APIRouter()


@router.get("/catalog/")
async def get_catalog(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort: str = Query(None, regex="^(name|uid)$"),
):

    raw_query_string = request.scope["query_string"].decode("utf-8")

    filters, ranges, name, sort = await parse_query_params(raw_query_string)

    crud = ProductCRUD(session)

    products, total = await crud.filter_products(
        filters, ranges, name, sort, page, page_size
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "products": products,
    }


@router.get("/catalog/filter/")
async def filter_catalog(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    raw_query_string = request.scope["query_string"].decode("utf-8")
    filters, ranges, _, _ = parse_query_params(raw_query_string)

    crud = ProductCRUD(session)

    property_stats = await crud.get_filter_statistics(filters, ranges)

    total_count = sum(stats.count for stats in property_stats.values())

    return {
        "count": total_count,
        "properties": property_stats,
    }
