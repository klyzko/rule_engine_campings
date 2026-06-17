from symtable import Class
from domain.entities.shedule_ent import Shedule
from domain.repositories.ischedule_crud import IScheduleRepository

class shedule:
    def put(self,shedule:Shedule):
        IScheduleRepository.delete(shedule.campaign_id)
        res=IScheduleRepository.create(shedule)
        return res