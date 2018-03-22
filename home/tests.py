import os
from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'rbi.settings'
application = get_wsgi_application()

from rbi import models
import xlsxwriter
from dateutil import relativedelta
# newestProposal = models.RwAssessment.objects.filter(componentid= 14).order_by('-id')[0]
# print(newestProposal.id)

def getC_risk(idx):
    dataGeneral = {}
    ass = models.RwAssessment.objects.filter(componentid= idx).order_by('-id')
    if ass.count() != 0:
        newest = ass[0]
        component = models.ComponentMaster.objects.get(componentid= idx)
        if component.componenttypeid_id == 8 or component.componenttypeid_id == 12 or component.componenttypeid_id == 14 or component.componenttypeid_id == 15:
            isTank = 1
        else:
            isTank = 0
        equip = models.EquipmentMaster.objects.get(equipmentid= component.equipmentid_id)
        fcof = models.RwFullFcof.objects.get(id= newest.id)
        fpof = models.RwFullPof.objects.get(id= newest.id)


        dataGeneral['equipment_name'] = equip.equipmentname
        dataGeneral['equipment_desc'] = equip.equipmentdesc
        dataGeneral['equipment_type'] = models.EquipmentType.objects.get(equipmenttypeid= equip.equipmenttypeid_id).equipmenttypename
        dataGeneral['component_name'] = component.componentname
        dataGeneral['init_thinning'] = fpof.thinningap1
        dataGeneral['init_cracking'] = fpof.sccap1
        dataGeneral['init_other'] = fpof.htha_ap1 + fpof.brittleap1 + fpof.fatigueap1
        dataGeneral['init_pof'] = fpof.thinningap1 + fpof.sccap1 + fpof.htha_ap1 + fpof.brittleap1
        dataGeneral['ext_thinning'] = fpof.externalap1
        dataGeneral['pof_catalog'] = fpof.totaldfap1
        dataGeneral['pof_val'] = fpof.pofap1
        dataGeneral['risk'] = fpof.pofap1 * fcof.fcofvalue
        dataGeneral['risk_future'] = fpof.pofap2 * fcof.fcofvalue

        if isTank:
            data1 = models.RwCaTank.objects.get(id= newest.id)
            data2 = models.RwInputCaTank.objects.get(id=newest.id)
            dataGeneral['flamable'] = data1.component_damage_cost
            dataGeneral['inj'] = 0
            dataGeneral['business'] = data1.business_cost
            dataGeneral['env'] = data1.fc_environ
            dataGeneral['consequence'] = data1.consequence
            dataGeneral['fluid'] = data2.api_fluid
            dataGeneral['fluid_phase'] = 'Liquid'
        else:
            data1 = models.RwCaLevel1.objects.get(id=newest.id)
            data2 = models.RwInputCaLevel1.objects.get(id=newest.id)
            dataGeneral['flamable'] = data1.fc_cmd
            dataGeneral['inj'] = data1.fc_inj
            dataGeneral['business'] = data1.fc_prod
            dataGeneral['env'] = data1.fc_envi
            dataGeneral['consequence'] = data1.fc_total
            dataGeneral['fluid'] = data2.api_fluid
            dataGeneral['fluid_phase'] = data2.system
        return dataGeneral

def getE_risk(idx):
    riskE = []
    listComponent = models.ComponentMaster.objects.filter(equipmentid= idx)
    if listComponent.count() != 0:
        for com in listComponent:
            comRisk = getC_risk(com.componentid)
            riskE.append(comRisk)
        return riskE

def getF_risk(idx):
    riskF = []
    lisEquipment = models.EquipmentMaster.objects.filter(facilityid= idx)
    if lisEquipment.count() != 0:
        for eq in lisEquipment:
            riskF.append(getE_risk(eq.equipmentid))
        return riskF

def getS_risk(idx):
    riskS = []
    lisFacility = models.Facility.objects.filter(siteid= idx)
    if lisFacility.count() != 0:
        for fa in lisFacility:
            riskS.append(getF_risk(fa.facilityid))
        return riskS

def relat():
    insp = models.RwDamageMechanism.objects.filter(id_dm= 157)
    rel = (insp[0].inspduedate - insp[0].lastinspdate).days
    return round(rel/365,2)

