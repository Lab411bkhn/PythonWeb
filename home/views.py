from operator import eq

from django.shortcuts import render, render_to_response, redirect
from rbi.models import ApiComponentType
from rbi.models import Sites
from rbi.models import Facility,EquipmentMaster, ComponentMaster, EquipmentType, DesignCode, Manufacturer, ComponentType
from rbi.models import FacilityRiskTarget
from rbi.models import RwAssessment,RwEquipment,RwComponent,RwStream,RwExtcorTemperature, RwCoating, RwMaterial
from rbi.models import RwInputCaLevel1, RwCaLevel1, RwFullPof, RwFullFcof
from django.http import Http404, HttpResponse
from rbi.DM_CAL import DM_CAL
from rbi.CA_CAL import CA_NORMAL

from datetime import datetime

# Project Management Function
def home(request):
    return render(request, "page/home.html")
def login(request):
    return render(request, "page/login.html")
def signup(request):
    return render(request,"page/signup.html")
def contact(request):
    return render(request,"page/contac.html")


### New function
def newSite(request):
    data = {}
    error = {}
    if request.method == "POST":
        data['sitename'] = request.POST.get('sitename')
        count = Sites.objects.filter(sitename= data['sitename']).count()
        if(count > 0):
            error['exist'] = "This Site already exist!"
        else:
            if (not data['sitename']):
                error['empty'] = "Sites does not empty!"
            else:
                obj = Sites(sitename= data['sitename'])
                obj.save()
                return redirect('site_display')
    return  render(request,"home/new/newSite.html",{'error': error, 'obj': data})

def facility(request,siteid):
    try:
        data = Sites.objects.get(siteid = siteid)
        dataFacility = {}
        error = {}
        if request.method == "POST":
            dataFacility['facilityname'] = request.POST.get('FacilityName')
            dataFacility['siteid'] = siteid
            dataFacility['managementfactor'] = request.POST.get('ManagementSystemFactor')
            dataFacility['risktarget_fc'] = request.POST.get('Financial')
            dataFacility['risktarget_ac'] = request.POST.get('Area')
            countFaci = Facility.objects.filter(facilityname= dataFacility['facilityname']).count()
            if(not dataFacility['facilityname']):
                error['facilityname'] = "Facility does not empty!"
            if(not dataFacility['managementfactor']):
                error['managefactor'] = "Manage Factor does not empty!"
            if(not dataFacility['risktarget_fc']):
                error['TargetFC'] = "Finance Target does not empty!"
            if(not dataFacility['risktarget_ac']):
                error['TargetAC'] = "Area Target does not empty!"
            if(dataFacility['facilityname'] and dataFacility['managementfactor'] and dataFacility['risktarget_ac'] and dataFacility['risktarget_fc']):
                if countFaci == 0:
                    faci = Facility(facilityname= dataFacility['facilityname'],managementfactor= dataFacility['managementfactor'], siteid_id=siteid)
                    faci.save()
                    faciOb = Facility.objects.get(facilityname= dataFacility['facilityname'])
                    facility_target = FacilityRiskTarget(facilityid_id= faciOb.facilityid , risktarget_ac= dataFacility['risktarget_ac'],
                                                         risktarget_fc= dataFacility['risktarget_fc'])
                    facility_target.save()
                    return redirect('facilityDisplay', siteid)
                else:
                    error['exist'] = "This Facility already exists!"
    except Sites.DoesNotExist:
        raise  Http404
    return  render(request, "home/new/facility.html",{'site':data, 'error': error, 'facility':dataFacility})

def equipment(request, facilityname):
    try:
        dataFacility = Facility.objects.get(facilityid= facilityname)
        dataEquipmentType = EquipmentType.objects.all()
        dataDesignCode = DesignCode.objects.all()
        dataManufacture = Manufacturer.objects.all()
        error = {}
        data = {}
        data['commissiondate'] = ""
        if request.method == "POST":
            data['equipmentnumber'] = request.POST.get('equipmentNumber')
            data['equipmentname'] = request.POST.get('equipmentName')
            data['equipmenttypeid'] = request.POST.get('equipmentType')
            data['designcodeid'] = request.POST.get('designCode')
            data['site'] = request.POST.get('Site')
            data['facility'] = request.POST.get('Facility')
            data['manufactureid'] = request.POST.get('manufacture')
            data['commissiondate'] = request.POST.get('CommissionDate')
            data['pfdno'] = request.POST.get('PDFNo')
            data['processdescription'] = request.POST.get('processDescription')
            data['equipmentdesc']= request.POST.get('decription')
            equip = EquipmentMaster.objects.filter(equipmentnumber= data['equipmentnumber']).count()
            if not data['equipmentnumber']:
                error['equipmentNumber'] = "Equipment Number does not empty!"
            if not data['equipmentname']:
                error['equipmentName'] = "Equipment Name does not empty!"
            if not data['designcodeid']:
                error['designcode'] = "Design Code does not empty!"
            if not data['manufactureid']:
                error['manufacture'] = "Manufacture does not empty!"
            if not data['commissiondate']:
                error['commisiondate'] = "Commission Date does not empty!"
            if (data['equipmentnumber'] and data['equipmentname'] and data['designcodeid'] and data['manufactureid'] and data['commissiondate']):
                if equip > 0:
                    error['exist'] = "Equipment already exists! Please choose other Equipment Number!"
                else:
                    equipdata = EquipmentMaster(equipmentnumber= data['equipmentnumber'], equipmentname= data['equipmentname'], equipmenttypeid_id=EquipmentType.objects.get(equipmenttypename= data['equipmenttypeid']).equipmenttypeid,
                                                designcodeid_id= DesignCode.objects.get(designcode= data['designcodeid']).designcodeid, siteid_id= Sites.objects.get(sitename= data['site']).siteid, facilityid_id= Facility.objects.get(facilityname= data['facility']).facilityid,
                                                manufacturerid_id= Manufacturer.objects.get(manufacturername= data['manufactureid']).manufacturerid, commissiondate= data['commissiondate'], pfdno= data['pfdno'], processdescription= data['processdescription'], equipmentdesc= data['equipmentdesc'])
                    equipdata.save()
                    return redirect('equipment_display',facilityname)
    except Facility.DoesNotExist:
        raise Http404
    return render(request,"home/new/equipment.html", {'obj': dataFacility, 'equipmenttype': dataEquipmentType, 'designcode': dataDesignCode, 'manufacture': dataManufacture, 'error': error, 'equipment':data, 'commisiondate':data['commissiondate']})

def newDesigncode(request, facilityname):
    try:
        error = {}
        data = {}
        if request.method == "POST":
            data['designcode'] = request.POST.get('design_code_name')
            data['designcodeapp'] = request.POST.get('design_code_app')
            designcode = DesignCode.objects.filter(designcode= data['designcode']).count()
            if(not data['designcode']):
                error['designcode'] = "Design Code does not empty!"
            if(not data['designcodeapp']):
                error['designcodeapp'] = "Design Code App does not empty!"
            if(data['designcode'] and data['designcodeapp']):
                if(designcode > 0):
                    error['exist'] = "Design Code already exist!"
                else:
                    design =DesignCode(designcode= data['designcode'], designcodeapp= data['designcodeapp'])
                    design.save()
                    return redirect('designcodeDisplay',facilityname)
    except Facility.DoesNotExist:
        raise Http404
    return render(request, "home/new/newDesignCode.html",{'facilityid': facilityname, 'error': error,'design': data})

def newManufacture(request, facilityname):
    try:
        error = {}
        data = {}
        if(request.method == "POST"):
            data['manufacturername'] = request.POST.get('manufacture')
            manufac = Manufacturer.objects.filter(manufacturername= data['manufacturername']).count()
            if(manufac > 0):
                error['exist'] = "This Manufacture already exists!"
            else:
                if(not data['manufacturername']):
                    error['manufacture'] = "Manufacture does not empty!"
                else:
                    manu = Manufacturer(manufacturername= data['manufacturername'])
                    manu.save()
                    return redirect('manufactureDisplay', facilityname)
    except Facility.DoesNotExist:
        raise Http404
    return render(request, "home/new/newManufacture.html", {'facilityid': facilityname, 'error': error, 'manufacture':data})

def newcomponent(request,equipmentname):
    try:
        dataEq = EquipmentMaster.objects.get(equipmentid= equipmentname)
        dataComponentType = ComponentType.objects.all()
        dataApicomponent = ApiComponentType.objects.all()
        error = {}
        data = {}
        isedit = 0
        if request.method == "POST":
            data['equipmentNumber'] = request.POST.get('equipmentNub')
            data['equipmentType'] = request.POST.get('equipmentType')
            data['designCode'] = request.POST.get('designCode')
            data['site'] = request.POST.get('plant')
            data['facility'] = request.POST.get('facility')
            data['componentnumber'] = request.POST.get('componentNumer')
            data['componenttypeid'] = request.POST.get('componentType')
            data['apicomponenttypeid'] = request.POST.get('apiComponentType')
            data['componentname'] = request.POST.get('componentName')
            data['comRisk'] = request.POST.get('comRisk')
            data['componentdesc'] = request.POST.get('decription')
            if data['comRisk'] == "on":
                data['isequipmentlinked'] = 1
            else:
                data['isequipmentlinked'] = 0
            comnum = ComponentMaster.objects.filter(componentnumber= data['componentnumber']).count()
            if(not data['componentnumber']):
                error['componentNumber'] ="Component Number does not empty!"
            if(not data['componentname']):
                error['componentName'] = "Component Name does not empty!"
            if(data['componentnumber'] and data['componentname']):
                if(comnum > 0):
                    error['exist'] = "This Component already exists!"
                else:
                    com = ComponentMaster(componentnumber= data['componentnumber'], equipmentid_id=EquipmentMaster.objects.get(equipmentnumber= data['equipmentNumber']).equipmentid,
                                          componenttypeid= ComponentType.objects.get(componenttypename= data['componenttypeid']), componentname= data['componentname'],
                                          componentdesc= data['componentdesc'], apicomponenttypeid= ApiComponentType.objects.get(apicomponenttypename= data['apicomponenttypeid']).apicomponenttypeid,
                                          isequipmentlinked= data['isequipmentlinked'])
                    com.save()
                    return redirect('component_display', equipmentname)
    except EquipmentMaster.DoesNotExist:
        raise Http404
    return render(request,'home/new/component.html', {'obj': dataEq , 'componenttype': dataComponentType, 'api':dataApicomponent, 'component':data, 'error': error, 'isedit':isedit})

def newProposal(request, componentname):
    try:
        dataCom = ComponentMaster.objects.get(componentid= componentname)
        dataEq = EquipmentMaster.objects.get(equipmentid= dataCom.equipmentid_id)
        dataFaci = Facility.objects.get(facilityid= dataEq.facilityid_id)
        api = ApiComponentType.objects.get(apicomponenttypeid= dataCom.apicomponenttypeid)
        commisiondate = dataEq.commissiondate.date().strftime('%Y-%m-%d')
        data ={}
        error = {}
        Fluid = ["Acid","AlCl3","C1-C2","C13-C16","C17-C25","C25+","C3-C4","C5", "C6-C8","C9-C12","CO","DEE","EE","EEA","EG","EO","H2","H2S","HCl","HF","Methanol","Nitric Acid","NO2","Phosgene","PO","Pyrophoric","Steam","Styrene","TDI","Water"]
        data['islink'] = dataCom.isequipmentlinked
        if request.method =="POST":
            data['assessmentname'] = request.POST.get('AssessmentName')
            data['assessmentdate'] = request.POST.get('assessmentdate')
            data['riskperiod']=request.POST.get('RiskAnalysisPeriod')
            if not data['assessmentname']:
                error['assessmentname'] = "Assessment Name does not empty"
            if not data['assessmentdate']:
                error['assessmentdate']= "Assesment Date does not empty!"

            if request.POST.get('adminControlUpset') == "on":
                adminControlUpset = 1
            else:
                adminControlUpset = 0

            if request.POST.get('ContainsDeadlegs') == "on":
                containsDeadlegs = 1
            else:
                containsDeadlegs = 0

            if request.POST.get('Highly') == "on":
                HighlyEffe = 1
            else:
                HighlyEffe = 0

            if request.POST.get('CylicOper') == "on":
                cylicOP = 1
            else:
                cylicOP = 0

            if request.POST.get('Downtime') == "on":
                downtime = 1
            else:
                downtime = 0

            if request.POST.get('SteamedOut') == "on":
                steamOut = 1
            else:
                steamOut = 0

            if request.POST.get('HeatTraced') == "on":
                heatTrace = 1
            else:
                heatTrace = 0

            if request.POST.get('PWHT') == "on":
                pwht = 1
            else:
                pwht = 0

            if request.POST.get('InterfaceSoilWater') == "on":
                interfaceSoilWater = 1
            else:
                interfaceSoilWater = 0

            if request.POST.get('PressurisationControlled') == "on":
                pressureControl = 1
            else:
                pressureControl = 0

            if request.POST.get('LOM') == "on":
                linerOnlineMoniter = 1
            else:
                linerOnlineMoniter = 0

            if request.POST.get('EquOper') == "on":
                lowestTemp = 1
            else:
                lowestTemp = 0

            if request.POST.get('PresenceofSulphidesShutdow') == "on":
                presentSulphidesShutdown =1
            else:
                presentSulphidesShutdown = 0

            if request.POST.get('MFTF') == "on":
                materialExposed = 1
            else:
                materialExposed = 0

            if request.POST.get('PresenceofSulphides') == "on":
                presentSulphide = 1
            else:
                presentSulphide = 0

            data['minTemp'] = request.POST.get('Min')
            data['ExternalEnvironment'] = request.POST.get('ExternalEnvironment')
            data['ThermalHistory'] = request.POST.get('ThermalHistory')
            data['OnlineMonitoring'] = request.POST.get('OnlineMonitoring')
            data['EquipmentVolumn'] = request.POST.get('EquipmentVolume')

            data['normaldiameter'] = request.POST.get('NominalDiameter')
            data['normalthick'] = request.POST.get('NominalThickness')
            data['currentthick'] = request.POST.get('CurrentThickness')
            data['tmin'] = request.POST.get('tmin')
            data['currentrate'] = request.POST.get('CurrentRate')
            data['deltafatt'] = request.POST.get('DeltaFATT')

            if request.POST.get('DFDI') == "on":
                damageDuringInsp = 1
            else:
                damageDuringInsp = 0

            if request.POST.get('ChemicalInjection') == "on":
                chemicalInj = 1
            else:
                chemicalInj = 0

            if request.POST.get('PresenceCracks') == "on":
                crackpresent = 1
            else:
                crackpresent = 0

            if request.POST.get('HFICI') == "on":
                HFICI = 1
            else:
                HFICI = 0

            if request.POST.get('TrampElements') == "on":
                TrampElement = 1
            else:
                TrampElement = 0

            data['MaxBrinell'] = request.POST.get('MBHW')
            data['complex'] = request.POST.get('ComplexityProtrusions')
            data['CylicLoad'] = request.POST.get('CLC')
            data['branchDiameter'] = request.POST.get('BranchDiameter')
            data['joinTypeBranch'] = request.POST.get('JTB')
            data['numberPipe'] = request.POST.get('NFP')
            data['pipeCondition'] = request.POST.get('PipeCondition')
            data['prevFailure'] = request.POST.get('PreviousFailures')

            if request.POST.get('VASD') == "on":
                visibleSharkingProtect = 1
            else:
                visibleSharkingProtect = 0

            data['shakingPipe'] = request.POST.get('ASP')
            data['timeShakingPipe'] = request.POST.get('ATSP')
            data['correctActionMitigate'] = request.POST.get('CAMV')

            # OP condition
            data['maxOT'] = request.POST.get('MaxOT')
            data['maxOP'] = request.POST.get('MaxOP')
            data['minOT'] = request.POST.get('MinOT')
            data['minOP'] = request.POST.get('MinOP')
            data['OpHydroPressure'] = request.POST.get('OHPP')
            data['FlowRate'] = request.POST.get('FlowRate')
            data['criticalTemp'] = request.POST.get('CET')
            data['OP1'] = request.POST.get('Operating1')
            data['OP2'] = request.POST.get('Operating2')
            data['OP3'] = request.POST.get('Operating3')
            data['OP4'] = request.POST.get('Operating4')
            data['OP5'] = request.POST.get('Operating5')
            data['OP6'] = request.POST.get('Operating6')
            data['OP7'] = request.POST.get('Operating7')
            data['OP8'] = request.POST.get('Operating8')
            data['OP9'] = request.POST.get('Operating9')
            data['OP10'] = request.POST.get('Operating10')

            #material
            data['material'] = request.POST.get('Material')
            data['maxDesignTemp'] = request.POST.get('MaxDesignTemp')
            data['minDesignTemp'] = request.POST.get('MinDesignTemp')
            data['designPressure'] = request.POST.get('DesignPressure')
            data['tempRef'] = request.POST.get('ReferenceTemperature')
            data['allowStress'] = request.POST.get('ASAT')
            data['BrittleFacture'] = request.POST.get('BFGT')
            data['CA'] = request.POST.get('CorrosionAllowance')
            data['sigmaPhase'] = request.POST.get('SigmaPhase')
            if request.POST.get('CoLAS') == "on":
                cacbonAlloy = 1
            else:
                cacbonAlloy = 0

            if request.POST.get('AusteniticSteel') == "on":
                austeniticStell = 1
            else:
                austeniticStell = 0

            if request.POST.get('SusceptibleTemper') == "on":
                suscepTemp = 1
            else:
                suscepTemp = 0

            if request.POST.get('NickelAlloy') == "on":
                nickelAlloy = 1
            else:
                nickelAlloy = 0

            if request.POST.get('Chromium') == "on":
                chromium = 1
            else:
                chromium = 0

            data['sulfurContent'] = request.POST.get('SulfurContent')
            data['heatTreatment'] = request.POST.get('heatTreatment')

            if request.POST.get('MGTEHTHA') == "on":
                materialHTHA = 1
            else:
                materialHTHA = 0

            data['HTHAMaterialGrade'] = request.POST.get('HTHAMaterialGrade')

            if request.POST.get('MaterialPTA') == "on":
                materialPTA = 1
            else:
                materialPTA = 0

            data['PTAMaterialGrade'] = request.POST.get('PTAMaterialGrade')
            data['materialCostFactor'] = request.POST.get('MaterialCostFactor')

            #Coating, Clading
            if request.POST.get('InternalCoating') == "on":
                InternalCoating = 1
            else:
                InternalCoating = 0

            if request.POST.get('ExternalCoating') == "on":
                ExternalCoating = 1
            else:
                ExternalCoating = 0

            data['ExternalCoatingID'] = request.POST.get('ExternalCoatingID')
            data['ExternalCoatingQuality'] = request.POST.get('ExternalCoatingQuality')

            if request.POST.get('SCWD') == "on":
                supportMaterial = 1
            else:
                supportMaterial = 0

            if request.POST.get('InternalCladding') == "on":
                InternalCladding = 1
            else:
                InternalCladding = 0

            data['CladdingCorrosionRate'] = request.POST.get('CladdingCorrosionRate')

            if request.POST.get('InternalLining') == "on":
                InternalLining = 1
            else:
                InternalLining = 0

            data['InternalLinerType'] = request.POST.get('InternalLinerType')
            data['InternalLinerCondition'] = request.POST.get('InternalLinerCondition')

            if request.POST.get('ExternalInsulation')== "on":
                ExternalInsulation = 1
            else:
                ExternalInsulation = 0

            if request.POST.get('ICC') == "on":
                InsulationCholride = 1
            else:
                InsulationCholride = 0

            data['ExternalInsulationType'] = request.POST.get('ExternalInsulationType')
            data['InsulationCondition'] = request.POST.get('InsulationCondition')

            # Steam
            data['NaOHConcentration'] = request.POST.get('NaOHConcentration')
            data['ReleasePercentToxic'] = request.POST.get('RFPT')
            data['ChlorideIon'] = request.POST.get('ChlorideIon')
            data['CO3'] = request.POST.get('CO3')
            data['H2SContent'] = request.POST.get('H2SContent')
            data['PHWater'] = request.POST.get('PHWater')

            if request.POST.get('EAGTA') == "on":
                exposureAcid = 1
            else:
                exposureAcid = 0

            if request.POST.get('ToxicConstituents') == "on":
                ToxicConstituents = 1
            else:
                ToxicConstituents = 0

            data['ExposureAmine'] = request.POST.get('ExposureAmine')
            data['AminSolution'] = request.POST.get('ASC')

            if request.POST.get('APDO') == "on":
                aquaDuringOP = 1
            else:
                aquaDuringOP = 0

            if request.POST.get('APDSD') == "on":
                aquaDuringShutdown = 1
            else:
                aquaDuringShutdown = 0

            if request.POST.get('EnvironmentCH2S') == "on":
                EnvironmentCH2S = 1
            else:
                EnvironmentCH2S = 0

            if request.POST.get('PHA') == "on":
                presentHF = 1
            else:
                presentHF = 0

            if request.POST.get('PresenceCyanides') == "on":
                presentCyanide = 1
            else:
                presentCyanide = 0

            if request.POST.get('PCH') == "on":
                processHydrogen = 1
            else:
                processHydrogen = 0

            if request.POST.get('ECCAC') == "on":
                environCaustic = 1
            else:
                environCaustic = 0

            if request.POST.get('ESBC') == "on":
                exposedSulfur = 1
            else:
                exposedSulfur = 0

            if request.POST.get('MEFMSCC') == "on":
                materialExposedFluid = 1
            else:
                materialExposedFluid = 0

            # CA
            data['APIFluid'] = request.POST.get('APIFluid')
            data['MassInventory'] = request.POST.get('MassInventory')
            data['Systerm'] = request.POST.get('Systerm')
            data['MassComponent'] = request.POST.get('MassComponent')
            data['EquipmentCost'] = request.POST.get('EquipmentCost')
            data['MittigationSysterm'] = request.POST.get('MittigationSysterm')
            data['ProductionCost'] = request.POST.get('ProductionCost')
            data['ToxicPercent'] = request.POST.get('ToxicPercent')
            data['InjureCost'] = request.POST.get('InjureCost')
            data['ReleaseDuration'] = request.POST.get('ReleaseDuration')
            data['EnvironmentCost'] = request.POST.get('EnvironmentCost')
            data['PersonDensity'] = request.POST.get('PersonDensity')
            data['DetectionType'] = request.POST.get('DetectionType')
            data['IsulationType'] = request.POST.get('IsulationType')

            rwassessment = RwAssessment(equipmentid= dataEq, componentid= dataCom, assessmentdate=data['assessmentdate'],
                                        riskanalysisperiod=data['riskperiod'],isequipmentlinked=data['islink'],proposalname=data['assessmentname'])
            rwassessment.save()

            rwequipment = RwEquipment(id= rwassessment, commissiondate= data['assessmentdate'], adminupsetmanagement= 1)
            rwequipment.save()


            rwcomponent =RwComponent(id = rwassessment, nominaldiameter=data['normaldiameter'], nominalthickness= data['normalthick'],
                                     minreqthickness=data['tmin'], currentcorrosionrate=data['currentrate'],deltafatt= data['deltafatt'])
            rwcomponent.save()

            rwstream = RwStream(id = rwassessment)
            rwstream.save()

            rwexcor = RwExtcorTemperature(id= rwassessment)
            rwexcor.save()

            rwcoat = RwCoating(id= rwassessment)
            rwcoat.save()


            rwmaterial = RwMaterial(id = rwassessment, corrosionallowance=data['CA'])
            rwmaterial.save()

            rwinputca = RwInputCaLevel1(id= rwassessment)
            rwinputca.save()

            dm_cal = DM_CAL(APIComponentType= "COLBTM",
                 Diametter= float(data['normaldiameter']), NomalThick=float(data['normalthick']), CurrentThick=float(data['currentthick']), MinThickReq=float(data['tmin']), CorrosionRate=float(data['currentrate']), CA=float(data['CA']),
                 ProtectedBarrier=False, CladdingCorrosionRate=0, InternalCladding=False, NoINSP_THINNING=1,
                 EFF_THIN="B", OnlineMonitoring="", HighlyEffectDeadleg=False, ContainsDeadlegs=False,
                 TankMaintain653=False, AdjustmentSettle="", ComponentIsWeld=False,
                 LinningType="", LINNER_ONLINE=False, LINNER_CONDITION="", YEAR_IN_SERVICE=0, INTERNAL_LINNING=False,
                 CAUSTIC_INSP_EFF="E", CAUSTIC_INSP_NUM=0, HEAT_TREATMENT="", NaOHConcentration=0, HEAT_TRACE=False,
                 STEAM_OUT=False,
                 AMINE_INSP_EFF="E", AMINE_INSP_NUM=0, AMINE_EXPOSED=False, AMINE_SOLUTION="",
                 ENVIRONMENT_H2S_CONTENT=False, AQUEOUS_OPERATOR=False, AQUEOUS_SHUTDOWN=False, SULPHIDE_INSP_EFF="E",
                 SULPHIDE_INSP_NUM=0, H2SContent=0, PH=0, PRESENT_CYANIDE=False, BRINNEL_HARDNESS="",
                 SULFUR_INSP_EFF="E", SULFUR_INSP_NUM=0, SULFUR_CONTENT="",
                 CACBONATE_INSP_EFF="E", CACBONATE_INSP_NUM=0, CO3_CONTENT=0,
                 PTA_SUSCEP=False, NICKEL_ALLOY=False, EXPOSED_SULFUR=False, PTA_INSP_EFF="E", PTA_INSP_NUM=0,
                 ExposedSH2OOperation=False, ExposedSH2OShutdown=False, ThermalHistory="", PTAMaterial="",
                 DOWNTIME_PROTECTED=False,
                 INTERNAL_EXPOSED_FLUID_MIST=False, EXTERNAL_EXPOSED_FLUID_MIST=False, CHLORIDE_ION_CONTENT=0,
                 CLSCC_INSP_EFF="E", CLSCC_INSP_NUM=0,
                 HSC_HF_INSP_EFF="E", HSC_HF_INSP_NUM=0,
                 HICSOHIC_INSP_EFF="E", HICSOHIC_INSP_NUM=0, HF_PRESENT=False,
                 EXTERNAL_INSP_NUM=0, EXTERNAL_INSP_EFF="E",
                 INTERFACE_SOIL_WATER=False, SUPPORT_COATING=False, INSULATION_TYPE="", CUI_INSP_NUM=0,
                 CUI_INSP_EFF="E", CUI_INSP_DATE=datetime.now().date(), CUI_PERCENT_1=0, CUI_PERCENT_2=0,
                 CUI_PERCENT_3=0, CUI_PERCENT_4=0, CUI_PERCENT_5=0, CUI_PERCENT_6=0, CUI_PERCENT_7=0, CUI_PERCENT_8=0,
                 CUI_PERCENT_9=0, CUI_PERCENT_10=0,
                 EXTERN_CLSCC_INSP_NUM=0, EXTERN_CLSCC_INSP_EFF="E",
                 EXTERNAL_INSULATION=False, COMPONENT_INSTALL_DATE=datetime.now().date(), CRACK_PRESENT=False,
                 EXTERNAL_EVIRONMENT="", EXTERN_COAT_QUALITY="", EXTERN_CLSCC_CUI_INSP_NUM=0,
                 EXTERN_CLSCC_CUI_INSP_EFF="E", PIPING_COMPLEXITY="", INSULATION_CONDITION="",
                 INSULATION_CHLORIDE=False,
                 MATERIAL_SUSCEP_HTHA=False, HTHA_MATERIAL="", HTHA_NUM_INSP=0, HTHA_EFFECT="E", HTHA_PRESSURE=0,
                 CRITICAL_TEMP=0, DAMAGE_FOUND=False,
                 LOWEST_TEMP=False,
                 TEMPER_SUSCEP=False, PWHT=False, BRITTLE_THICK=0, CARBON_ALLOY=False, DELTA_FATT=0,
                 MAX_OP_TEMP=0, CHROMIUM_12=False, MIN_OP_TEMP=0, MIN_DESIGN_TEMP=0, REF_TEMP=0,
                 AUSTENITIC_STEEL=False, PERCENT_SIGMA=0,
                 EquipmentType="", PREVIOUS_FAIL="", AMOUNT_SHAKING="", TIME_SHAKING="", CYLIC_LOAD="",
                 CORRECT_ACTION="", NUM_PIPE="", PIPE_CONDITION="", JOINT_TYPE="", BRANCH_DIAMETER="")

            ca_cal = CA_NORMAL(NominalDiametter = float(request.POST.get('NominalDiameter')), MATERIAL_COST = 1, FLUID = "C3-C4", FLUID_PHASE = "Liquid", API_COMPONENT_TYPE_NAME ="COLBTM", DETECTION_TYPE = "C",
                 ISULATION_TYPE = "C", STORED_PRESSURE = 102, ATMOSPHERIC_PRESSURE = 101, STORED_TEMP = 27, MASS_INVERT = 181528,
                 MASS_COMPONENT = 12154, MITIGATION_SYSTEM = "", TOXIC_PERCENT = 0, RELEASE_DURATION = "", PRODUCTION_COST = 50000,
                 INJURE_COST = 5000000, ENVIRON_COST = 0, PERSON_DENSITY = 0.0005, EQUIPMENT_COST = 1200, TOXIC_PHASE = "")

            refullPOF = RwFullPof(id= rwassessment, thinningap1= dm_cal.DFB_THIN(5.08), thinningap2= dm_cal.DFB_THIN(8.08), thinningap3= dm_cal.DFB_THIN(11.08))
            refullPOF.save()

            refullfc = RwFullFcof(id= rwassessment, envcost=0)
            refullfc.save()

            calv1 = RwCaLevel1(id= rwassessment, release_phase= ca_cal.GET_RELEASE_PHASE(), fact_di= ca_cal.fact_di(), ca_inj_flame= ca_cal.ca_inj_flame(),
                               fact_mit= ca_cal.fact_mit(), fact_ait= ca_cal.fact_ait(), ca_cmd= ca_cal.ca_cmd(), fc_cmd= ca_cal.fc_cmd(),
                               fc_affa= ca_cal.fc_affa(), fc_envi= ca_cal.fc_environ(), fc_prod= ca_cal.fc_prod(), fc_inj= ca_cal.fc_inj(),
                               fc_total= ca_cal.fc(), fcof_category= ca_cal.FC_Category(ca_cal.fc()))
            calv1.save()

            return redirect('resultca', rwassessment.id)
    except ComponentMaster.DoesNotExist:
        raise Http404
    return render(request, 'home/new/Normal.html',{'facility': dataFaci,'component': dataCom , 'equipment':dataEq,'api':api,'commissiondate': commisiondate,'dataLink': data['islink'], 'fluid': Fluid})

### Edit function
def editSite(request, sitename):
     try:
        data = Sites.objects.get(siteid= sitename)
        error = {}
        datatemp ={}
        if request.method == "POST":
            datatemp['sitename'] = request.POST.get('sitename')
            if (not datatemp['sitename']):
                error['empty'] = "Sites does not empty!"
            else:
                if data.sitename != datatemp['sitename'] and Sites.objects.filter(sitename= datatemp['sitename']).count() > 0:
                    error['exist'] = "This Site already exist!"
                else:
                    data.sitename = datatemp['sitename']
                    data.save()
                    return redirect('site_display')
     except Sites.DoesNotExist:
         raise Http404
     return render(request,'home/new/newSite.html', {'obj':data, 'error':error});

def editFacility(request, sitename, facilityname):
    try:
        datafaci = Facility.objects.get(facilityid= facilityname)
        dataTarget = FacilityRiskTarget.objects.get(facilityid= facilityname)
        data = Sites.objects.get(siteid=sitename)
        dataFacility = {}
        dataFacility['facilityname'] = datafaci.facilityname
        dataFacility['managementfactor'] = datafaci.managementfactor
        dataFacility['risktarget_fc'] = dataTarget.risktarget_fc
        dataFacility['risktarget_ac'] = dataTarget.risktarget_ac
        error = {}
        if request.method == "POST":
            dataFacility['facilityname'] = request.POST.get('FacilityName')
            dataFacility['siteid'] = sitename
            dataFacility['managementfactor'] = request.POST.get('ManagementSystemFactor')
            dataFacility['risktarget_fc'] = request.POST.get('Financial')
            dataFacility['risktarget_ac'] = request.POST.get('Area')
            if (not dataFacility['facilityname']):
                error['facilityname'] = "Facility does not empty!"
            if (not dataFacility['managementfactor']):
                error['managefactor'] = "Manage Factor does not empty!"
            if (not dataFacility['risktarget_fc']):
                error['TargetFC'] = "Finance Target does not empty!"
            if (not dataFacility['risktarget_ac']):
                error['TargetAC'] = "Area Target does not empty!"
            if (dataFacility['facilityname'] and dataFacility['managementfactor'] and dataFacility['risktarget_ac'] and
                    dataFacility['risktarget_fc']):
                if datafaci.facilityname !=  dataFacility['facilityname'] and Facility.objects.filter(facilityname= dataFacility['facilityname']).count() >0:
                    error['exist'] = "This Facility already exist!"
                else:
                    datafaci.facilityname = dataFacility['facilityname']
                    datafaci.managementfactor = dataFacility['managementfactor']
                    datafaci.save()
                    facility_target = FacilityRiskTarget.objects.get(facilityid= datafaci.facilityid)
                    facility_target.risktarget_ac = dataFacility['risktarget_ac']
                    facility_target.risktarget_fc = dataFacility['risktarget_fc']
                    facility_target.save()
                    return redirect('facilityDisplay', sitename)
    except Facility.DoesNotExist:
        raise Http404
    return render(request, 'home/new/facility.html', {'facility': dataFacility, 'site': data, 'error':error})

def editEquipment(request,facilityname,equipmentname):
    try:
        dataFacility = Facility.objects.get(facilityid=facilityname)
        data = EquipmentMaster.objects.get(equipmentid= equipmentname)
        commisiondate = data.commissiondate.date().strftime('%Y-%m-%d')
        dataEquipmentType = EquipmentType.objects.all()
        dataDesignCode = DesignCode.objects.all()
        dataManufacture = Manufacturer.objects.all()
        dataEq = {}
        error = {}
        if request.method == "POST":
            dataEq['equipmentnumber'] = request.POST.get('equipmentNumber')
            dataEq['equipmentname'] = request.POST.get('equipmentName')
            dataEq['equipmenttype'] = request.POST.get('equipmentType')
            dataEq['designcode'] = request.POST.get('designCode')
            dataEq['manufacture'] = request.POST.get('manufacture')
            dataEq['commisiondate'] = request.POST.get('CommissionDate')
            dataEq['pfdno'] = request.POST.get('PDFNo')
            dataEq['description'] = request.POST.get('decription')
            dataEq['processdescription'] = request.POST.get('processDescription')

            if not dataEq['equipmentnumber']:
                error['equipmentNumber'] = "Equipment Number does not empty!"
            if not dataEq['equipmentname']:
                error['equipmentName'] = "Equipment Name does not empty!"
            if not dataEq['designcode']:
                error['designcode'] = "Design Code does not empty!"
            if not dataEq['manufacture']:
                error['manufacture'] = "Manufacture does not empty!"
            if not dataEq['commisiondate']:
                error['commisiondate'] = "Commission Date does not empty!"
            if dataEq['equipmentnumber'] and dataEq['equipmentname'] and dataEq['designcode'] and dataEq['manufacture'] and dataEq['commisiondate']:
                if EquipmentMaster.objects.filter(equipmentnumber= dataEq['equipmentnumber']).count() > 0 and data.equipmentnumber != dataEq['equipmentnumber']:
                    error['exist'] = "Equipment already exists!"
                else:
                    data.equipmentnumber = dataEq['equipmentnumber']
                    data.equipmentname = dataEq['equipmentname']
                    data.equipmenttypeid = EquipmentType.objects.get(equipmenttypename= dataEq['equipmenttype'])
                    data.designcodeid = DesignCode.objects.get(designcode= dataEq['designcode'])
                    data.manufacturerid = Manufacturer.objects.get(manufacturername= dataEq['manufacture'])
                    data.commissiondate = dataEq['commisiondate']
                    data.pfdno = dataEq['pfdno']
                    data.equipmentdesc = dataEq['description']
                    data.processdescription = dataEq['processdescription']
                    data.save()
                    return redirect('equipment_display', facilityname)
    except EquipmentMaster.DoesNotExist:
        raise Http404
    return render(request, 'home/new/equipment.html', {'equipment':data, 'obj':dataFacility, 'commisiondate':commisiondate,'equipmenttype': dataEquipmentType, 'designcode': dataDesignCode, 'manufacture': dataManufacture, 'error':error})

def editComponent(request, equipmentname,componentname):
    try:
        data = ComponentMaster.objects.get(componentid= componentname)
        dataEquip = EquipmentMaster.objects.get(equipmentid= equipmentname)
        dataComponentType = ComponentType.objects.all()
        dataApicomponent = ApiComponentType.objects.all()
        dataCom = {}
        error = {}
        isEdit = 1;
        if request.method == "POST":
            dataCom['componentnumber'] = request.POST.get('componentNumer')
            dataCom['componenttype'] = request.POST.get('componentType')
            dataCom['apicomponenttype'] = request.POST.get('apiComponentType')
            dataCom['componentname'] = request.POST.get('componentName')
            dataCom['isequipmentlink'] = request.POST.get('comRisk')
            dataCom['descrip'] = request.POST.get('decription')
            if dataCom['isequipmentlink'] == "on":
                islink = 1
            else:
                islink = 0
            if (not dataCom['componentnumber']):
                error['componentNumber'] = "Component Number does not empty!"
            if (not dataCom['componentname']):
                error['componentName'] = "Component Name does not empty!"
            if dataCom['componentnumber'] and dataCom['componentname']:
                if ComponentMaster.objects.filter(componentnumber= dataCom['componentnumber']).count()>0 and data.componentnumber != dataCom['componentnumber']:
                    error['exist'] = "This Component already exist!"
                else:
                    data.componentnumber = dataCom['componentnumber']
                    data.componentname = dataCom['componentname']
                    data.componenttypeid = ComponentType.objects.get(componenttypename=dataCom['componenttype'])
                    data.isequipmentlinked = islink
                    data.componentdesc = dataCom['descrip']
                    data.save()
                    return  redirect('component_display', equipmentname)
    except ComponentMaster.DoesNotExist:
        raise Http404
    return render(request, 'home/new/component.html', {'obj': dataEquip , 'componenttype': dataComponentType, 'api':dataApicomponent,'component':data, 'isedit':isEdit})

def editDesignCode(request, facilityname,designcodeid):
    try:
        data = DesignCode.objects.get(designcodeid= designcodeid)
        dataDesign = {}
        error = {}
        if request.method == "POST":
            dataDesign['designcode'] = request.POST.get('design_code_name')
            dataDesign['designcodeapp'] = request.POST.get('design_code_app')
            if not dataDesign['designcode']:
                error['designcode'] = "Design Code does not empty!"
            if not dataDesign['designcodeapp']:
                error['designcodeapp'] = "Design Code App does not empty!"
            if dataDesign['designcode'] and dataDesign['designcodeapp']:
                if DesignCode.objects.filter(designcode= dataDesign['designcode']).count() >0 and data.designcode != dataDesign['designcode']:
                    error['exist'] = "This Design Code already exist!"
                else:
                    data.designcode = dataDesign['designcode']
                    data.designcodeapp = dataDesign['designcodeapp']
                    data.save()
                    return redirect('designcodeDisplay', facilityname)
    except DesignCode.DoesNotExist:
        raise Http404
    return render(request, 'home/new/newDesignCode.html', {'design':data, 'facilityid':facilityname})

def editManufacture(request, facilityname,manufactureid):
    try:
        data = Manufacturer.objects.get(manufacturerid= manufactureid)
        dataManu = {}
        error = {}
        if request.method == "POST":
            dataManu['manufacturername'] = request.POST.get('manufacture')
            if not dataManu['manufacturername']:
                error['manufacture'] = "Manufacture does not empty!"
            if dataManu['manufacturername']:
                if Manufacturer.objects.filter(manufacturername= dataManu['manufacturername']).count()>0 and data.manufacturername != dataManu['manufacturername']:
                    error['exist'] = "This Manufacture already exists!"
                else:
                    data.manufacturername = dataManu['manufacturername']
                    data.save()
                    return redirect('manufactureDisplay', facilityname)
    except Manufacturer.DoesNotExist:
        raise Http404
    return render(request, 'home/new/newManufacture.html', {'manufacture': data, 'facilityid': facilityname, 'error': error})

### Display function
def site_display(request):
    data = Sites.objects.all()
    if "_delete" in request.POST:
        for a in data:
            if(request.POST.get('%d' %a.siteid)):
                a.delete()
        return redirect('site_display')
    elif "_edit" in request.POST:
        for a in data:
            if(request.POST.get('%d' %a.siteid)):
                return redirect('editsite', a.siteid)
    return render(request,'display/site_display.html',{'obj':data})

def facilityDisplay(request, sitename):
    try:
        count = Facility.objects.filter(siteid= sitename).count()
        if( count > 0):
            data = Facility.objects.filter(siteid = sitename)
        else:
            data = {}
        if "_edit" in request.POST:
            for a in data:
                if(request.POST.get('%d' %a.facilityid)):
                    return redirect('editfacility', sitename= sitename, facilityname= a.facilityid)
        elif "_delete" in request.POST:
            for a in data:
                if(request.POST.get('%d' %a.facilityid)):
                    a.delete()
            return redirect('facilityDisplay', sitename)
    except Sites.DoesNotExist:
        raise  Http404
    return render(request, 'display/facility_display.html', {'obj':data, 'c': sitename})

def equipmentDisplay(request, facilityname):
    try:
        sitename = Facility.objects.get(facilityid= facilityname).siteid_id;
        count = EquipmentMaster.objects.filter(facilityid = facilityname).count()
        if(count > 0):
            data = EquipmentMaster.objects.filter(facilityid=facilityname)
        else:
            data = {}
        if "_edit" in request.POST:
            for a in data:
                if request.POST.get('%d' %a.equipmentid):
                    return redirect('editequipment', facilityname= facilityname, equipmentname= a.equipmentid)
        elif "_delete" in request.POST:
            for a in data:
                if request.POST.get('%d' %a.equipmentid):
                    a.delete()
            return redirect('equipment_display', facilityname)
    except Facility.DoesNotExist:
        raise Http404
    return render(request, 'display/equipment_display.html', {'obj':data , 'facilityid':facilityname, 'sitename': sitename})

def componentDisplay(request, equipmentname):
    try:
        dataEq = EquipmentMaster.objects.get(equipmentid=equipmentname)
        countCom = ComponentMaster.objects.filter(equipmentid= equipmentname).count()
        if(countCom > 0):
            dataCom = ComponentMaster.objects.filter(equipmentid= equipmentname)
        else:
            dataCom = {}
        if "_edit" in request.POST:
            for a in dataCom:
                if request.POST.get('%d' %a.componentid):
                    return redirect('editcomponent', equipmentname= equipmentname, componentname= a.componentid)
        elif "_delete" in request.POST:
            for a in dataCom:
                if request.POST.get('%d' %a.componentid):
                    a.delete()
            return redirect('component_display', equipmentname)
    except EquipmentMaster.DoesNotExist:
        raise Http404
    return render(request, 'display/component_display.html', {'obj':dataCom, 'equipment': dataEq})

def designcodeDisplay(request, facilityname):
    try:
        dataEq = Facility.objects.get(facilityid= facilityname)
        dataDesign = DesignCode.objects.all()
        if "_delete" in request.POST:
            for a in dataDesign:
                if request.POST.get('%d' %a.designcodeid):
                    a.delete()
            return redirect('designcodeDisplay', facilityname)
        elif "_edit" in request.POST:
            for a in dataDesign:
                if request.POST.get('%d' %a.designcodeid):
                    return redirect('editdesigncode', facilityname= facilityname, designcodeid= a.designcodeid)
    except Facility.DoesNotExist:
        raise Http404
    return render(request, 'display/designcode_display.html',{'designcode': dataDesign, 'facilityid': facilityname})

def manufactureDisplay(request, facilityname):
    try:
        dataEq = Facility.objects.get(facilityid= facilityname)
        datamanufacture = Manufacturer.objects.all()
        if "_edit" in request.POST:
            for a in datamanufacture:
                if request.POST.get('%d' %a.manufacturerid):
                    return redirect('editmanufacture', facilityname= facilityname, manufactureid= a.manufacturerid)
        elif "_delete" in request.POST:
            for a in datamanufacture:
                if request.POST.get('%d' %a.manufacturerid):
                    a.delete()
            return redirect('manufactureDisplay', facilityname)
    except Facility.DoesNotExist:
        raise Http404
    return render(request, 'display/manufacture_display.html',{'manufacture': datamanufacture, 'facilityid': facilityname})

def displayCA(request, proposalname):
    ca = RwCaLevel1.objects.get(id= proposalname)
    return render(request, 'display/CA.html', {'obj': ca})

def displayDF(request, proposalname):
    df = RwFullPof.objects.get(id= proposalname)
    return render(request, 'display/dfThinning.html', {'obj':df})