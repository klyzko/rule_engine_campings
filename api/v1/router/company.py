from fastapi import APIRouter, Depends, status, HTTPException
from api.v1.shemas.company_shemas import Company_create
from core.depend_pg import get_db

router = APIRouter(prefix='campaigns', tags=["company"])

@router.post()
def create_company(com: Company_create,db:Depends(get_db)):





