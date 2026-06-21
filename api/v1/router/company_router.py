from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from api.v1.shemas.company_shemas import Company_create, Company_update
from core.depend_pg import get_db
from infrastructure.repositories.company_crud_orm import SQLAlchemyCampaignRepository
from domain.repositories.icompany_crud import ICampaignRepository
from domain.entities.company_ent import Company
from core.depend_pg import get_db

router = APIRouter(prefix="/campaigns", tags=["company"])



@router.post("/", response_model=Company_create, status_code=status.HTTP_201_CREATED)
async def create_company(
    com: Company_create,
    session: AsyncSession = Depends(get_db)
):

    """Создание новой кампании"""
    company_ent=Company(**com.model_dump())
    bd=SQLAlchemyCampaignRepository(session)
    res=await bd.create(company_ent)
    return res



@router.get("/")
async def get_all_companies(
     limit: int = Query(10, ge=1, le=100),
     offset: int = Query(0, ge=0),
     session: AsyncSession = Depends(get_db)
):
     """Получение списка всех кампаний"""
     bd = SQLAlchemyCampaignRepository(session)
     res = await bd.get_all(limit=limit, offset=offset)
     return res


@router.get("/{company_id}")
async def get_company(
     company_id: UUID,
     session: AsyncSession = Depends(get_db)
 ):
     """Получение кампании по ID"""
     bd = SQLAlchemyCampaignRepository(session)
     res = await bd.get_by_id(company_id)
     if not res:
         raise HTTPException(status_code=404, detail="Company not found")
     return res
#
#
@router.patch("/{company_id}")
async def update_company(
     company_id: UUID,
     com: Company_update,
     session: AsyncSession = Depends(get_db)
 ):
     """Обновление кампании"""
     bd = SQLAlchemyCampaignRepository(session)
     company_ent = Company(**com.model_dump())
     company_ent.id = company_id
     print(company_ent)
     try:
         res= await bd.update(company_ent)
         return res
     except Exception as e:
         raise HTTPException(status_code=404, detail=e)
