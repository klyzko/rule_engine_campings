from fastapi import APIRouter, Depends, status, HTTPException
from api.v1.shemas.company_shemas import Company_create

router = APIRouter(prefix='campaigns', tags=["company"])

@router.post()
def create_company(com: Company_create):




