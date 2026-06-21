from symtable import Class
from domain.entities.shedule_ent import Shedule
from domain.repositories.ischedule_crud import IScheduleRepository
from typing import List

class shedule_logik:
    def __init__(self,sheddb:IScheduleRepository):
        self.sheddb=sheddb
    async def put(self,shedule:List[Shedule]):
       await self.sheddb.delete(shedule[0].campaign_id)
       res =[]
       for item in shedule:
        res.append(await self.sheddb.create(item))
       return res