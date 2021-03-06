from csv import excel
from operator import eq
from django.shortcuts import render, render_to_response, redirect
from rbi.models import ApiComponentType
from rbi.models import Sites
from rbi.models import Facility,EquipmentMaster, ComponentMaster, EquipmentType, DesignCode, Manufacturer, ComponentType
from rbi.models import FacilityRiskTarget
from rbi.models import RwAssessment,RwEquipment,RwComponent,RwStream,RwExtcorTemperature, RwCoating, RwMaterial
from rbi.models import RwInputCaLevel1, RwCaLevel1, RwFullPof, RwFullFcof, RwInputCaTank, RwCaTank, RwDamageMechanism, DmItems
from django.http import Http404, HttpResponse
from rbi.DM_CAL import DM_CAL
from rbi.CA_CAL import CA_NORMAL, CA_SHELL, CA_TANK_BOTTOM
from dateutil.relativedelta import relativedelta;
from datetime import datetime
import xlsxwriter
from io import BytesIO
from rbi.process.excel import export_data
from rbi.process.matrix import location

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
        tankapi =[6,7,8,9,10,11,12,13,14,15,36,38,39]
        other = []
        for a in dataApicomponent:
            if a.apicomponenttypeid not in tankapi:
                other.append(a)
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
    return render(request,'home/new/component.html', {'obj': dataEq , 'componenttype': dataComponentType, 'api':dataApicomponent, 'component':data, 'error': error, 'isedit':isedit, 'other':other})

def newProposal(request, componentname):
    try:
        dataCom = ComponentMaster.objects.get(componentid= componentname)
        dataEq = EquipmentMaster.objects.get(equipmentid= dataCom.equipmentid_id)
        dataFaci = Facility.objects.get(facilityid= dataEq.facilityid_id)
        dataFaciTarget = FacilityRiskTarget.objects.get(facilityid= dataEq.facilityid_id)
        api = ApiComponentType.objects.get(apicomponenttypeid= dataCom.apicomponenttypeid)
        commisiondate = dataEq.commissiondate.date().strftime('%Y-%m-%d')
        data ={}
        error = {}
        Fluid = ["Acid","AlCl3","C1-C2","C13-C16","C17-C25","C25+","C3-C4","C5", "C6-C8","C9-C12","CO","DEE","EE","EEA","EG","EO","H2","H2S","HCl","HF","Methanol","Nitric Acid","NO2","Phosgene","PO","Pyrophoric","Steam","Styrene","TDI","Water"]
        data['islink'] = dataCom.isequipmentlinked
        if request.method =="POST":
            data['assessmentname'] = request.POST.get('AssessmentName')
            data['assessmentdate'] = request.POST.get('assessmentdate')
            data['apicomponenttypeid'] = api.apicomponenttypename
            data['equipmentType'] = request.POST.get('EquipmentType')

            data['riskperiod']=request.POST.get('RiskAnalysisPeriod')
            if not data['assessmentname']:
                error['assessmentname'] = "Assessment Name does not empty"
            if not data['assessmentdate']:
                error['assessmentdate']= "Assesment Date does not empty!"

            if request.POST.get('adminControlUpset'):
                adminControlUpset = 1
            else:
                adminControlUpset = 0

            if request.POST.get('ContainsDeadlegs'):
                containsDeadlegs = 1
            else:
                containsDeadlegs = 0

            if request.POST.get('Highly'):
                HighlyEffe = 1
            else:
                HighlyEffe = 0

            if request.POST.get('CylicOper'):
                cylicOP = 1
            else:
                cylicOP = 0

            if request.POST.get('Downtime'):
                downtime = 1
            else:
                downtime = 0

            if request.POST.get('SteamedOut'):
                steamOut = 1
            else:
                steamOut = 0

            if request.POST.get('HeatTraced'):
                heatTrace = 1
            else:
                heatTrace = 0

            if request.POST.get('PWHT'):
                pwht = 1
            else:
                pwht = 0

            if request.POST.get('InterfaceSoilWater'):
                interfaceSoilWater = 1
            else:
                interfaceSoilWater = 0

            if request.POST.get('PressurisationControlled'):
                pressureControl = 1
            else:
                pressureControl = 0

            if request.POST.get('LOM'):
                linerOnlineMoniter = 1
            else:
                linerOnlineMoniter = 0

            if request.POST.get('EquOper'):
                lowestTemp = 1
            else:
                lowestTemp = 0

            if request.POST.get('PresenceofSulphidesShutdow'):
                presentSulphidesShutdown =1
            else:
                presentSulphidesShutdown = 0

            if request.POST.get('MFTF'):
                materialExposed = 1
            else:
                materialExposed = 0

            if request.POST.get('PresenceofSulphides'):
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

            if request.POST.get('DFDI'):
                damageDuringInsp = 1
            else:
                damageDuringInsp = 0

            if request.POST.get('ChemicalInjection'):
                chemicalInj = 1
            else:
                chemicalInj = 0

            if request.POST.get('PresenceCracks'):
                crackpresent = 1
            else:
                crackpresent = 0

            if request.POST.get('HFICI'):
                HFICI = 1
            else:
                HFICI = 0

            if request.POST.get('TrampElements'):
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

            if request.POST.get('VASD'):
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
            if request.POST.get('CoLAS'):
                cacbonAlloy = 1
            else:
                cacbonAlloy = 0

            if request.POST.get('AusteniticSteel'):
                austeniticStell = 1
            else:
                austeniticStell = 0

            if request.POST.get('SusceptibleTemper'):
                suscepTemp = 1
            else:
                suscepTemp = 0

            if request.POST.get('NickelAlloy'):
                nickelAlloy = 1
            else:
                nickelAlloy = 0

            if request.POST.get('Chromium'):
                chromium = 1
            else:
                chromium = 0

            data['sulfurContent'] = request.POST.get('SulfurContent')
            data['heatTreatment'] = request.POST.get('heatTreatment')

            if request.POST.get('MGTEHTHA'):
                materialHTHA = 1
            else:
                materialHTHA = 0

            data['HTHAMaterialGrade'] = request.POST.get('HTHAMaterialGrade')

            if request.POST.get('MaterialPTA'):
                materialPTA = 1
            else:
                materialPTA = 0

            data['PTAMaterialGrade'] = request.POST.get('PTAMaterialGrade')
            data['materialCostFactor'] = request.POST.get('MaterialCostFactor')

            #Coating, Clading
            if request.POST.get('InternalCoating'):
                InternalCoating = 1
            else:
                InternalCoating = 0

            if request.POST.get('ExternalCoating'):
                ExternalCoating = 1
            else:
                ExternalCoating = 0

            data['ExternalCoatingID'] = request.POST.get('ExternalCoatingID')
            data['ExternalCoatingQuality'] = request.POST.get('ExternalCoatingQuality')

            if request.POST.get('SCWD'):
                supportMaterial = 1
            else:
                supportMaterial = 0

            if request.POST.get('InternalCladding'):
                InternalCladding = 1
            else:
                InternalCladding = 0

            data['CladdingCorrosionRate'] = request.POST.get('CladdingCorrosionRate')

            if request.POST.get('InternalLining'):
                InternalLining = 1
            else:
                InternalLining = 0

            data['InternalLinerType'] = request.POST.get('InternalLinerType')
            data['InternalLinerCondition'] = request.POST.get('InternalLinerCondition')

            if request.POST.get('ExternalInsulation')== "on" or request.POST.get('ExternalInsulation')== 1:
                ExternalInsulation = 1
            else:
                ExternalInsulation = 0

            if request.POST.get('ICC'):
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

            if request.POST.get('EAGTA'):
                exposureAcid = 1
            else:
                exposureAcid = 0

            if request.POST.get('ToxicConstituents'):
                ToxicConstituents = 1
            else:
                ToxicConstituents = 0

            data['ExposureAmine'] = request.POST.get('ExposureAmine')
            data['AminSolution'] = request.POST.get('ASC')

            if request.POST.get('APDO'):
                aquaDuringOP = 1
            else:
                aquaDuringOP = 0

            if request.POST.get('APDSD'):
                aquaDuringShutdown = 1
            else:
                aquaDuringShutdown = 0

            if request.POST.get('EnvironmentCH2S'):
                EnvironmentCH2S = 1
            else:
                EnvironmentCH2S = 0

            if request.POST.get('PHA'):
                presentHF = 1
            else:
                presentHF = 0

            if request.POST.get('PresenceCyanides'):
                presentCyanide = 1
            else:
                presentCyanide = 0

            if request.POST.get('PCH'):
                processHydrogen = 1
            else:
                processHydrogen = 0

            if request.POST.get('ECCAC'):
                environCaustic = 1
            else:
                environCaustic = 0

            if request.POST.get('ESBC'):
                exposedSulfur = 1
            else:
                exposedSulfur = 0

            if request.POST.get('MEFMSCC'):
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

            rwequipment = RwEquipment(id= rwassessment, commissiondate= commisiondate, adminupsetmanagement= adminControlUpset, containsdeadlegs= containsDeadlegs,
                                      cyclicoperation= cylicOP, highlydeadleginsp= HighlyEffe, downtimeprotectionused= downtime, externalenvironment= data['ExternalEnvironment'],
                                      heattraced= heatTrace, interfacesoilwater= interfaceSoilWater, lineronlinemonitoring= linerOnlineMoniter, materialexposedtoclext= materialExposed,
                                      minreqtemperaturepressurisation= data['minTemp'], onlinemonitoring= data['OnlineMonitoring'], presencesulphideso2= presentSulphide, presencesulphideso2shutdown= presentSulphidesShutdown,
                                      pressurisationcontrolled= pressureControl, pwht= pwht, steamoutwaterflush= steamOut, managementfactor= dataFaci.managementfactor, thermalhistory= data['ThermalHistory'],
                                      yearlowestexptemp= lowestTemp, volume= data['EquipmentVolumn'])
            rwequipment.save()


            rwcomponent =RwComponent(id = rwassessment, nominaldiameter=data['normaldiameter'], nominalthickness= data['normalthick'], currentthickness= data['currentthick'],
                                     minreqthickness=data['tmin'], currentcorrosionrate=data['currentrate'], branchdiameter= data['branchDiameter'],branchjointtype= data['joinTypeBranch'],brinnelhardness= data['MaxBrinell']
                                     ,deltafatt= data['deltafatt'],chemicalinjection= chemicalInj, highlyinjectioninsp= HFICI, complexityprotrusion= data['complex'],correctiveaction= data['correctActionMitigate'],crackspresent= crackpresent,
                                     cyclicloadingwitin15_25m= data['CylicLoad'], damagefoundinspection= damageDuringInsp, numberpipefittings= data['numberPipe'],pipecondition= data['pipeCondition'],
                                     previousfailures= data['prevFailure'], shakingamount= data['shakingPipe'], shakingdetected= visibleSharkingProtect,shakingtime= data['timeShakingPipe'], trampelements= TrampElement)
            rwcomponent.save()

            rwstream = RwStream(id = rwassessment, aminesolution=data['AminSolution'], aqueousoperation= aquaDuringOP, aqueousshutdown= aquaDuringShutdown, toxicconstituent= ToxicConstituents, caustic= environCaustic,
                                chloride= data['ChlorideIon'], co3concentration= data['CO3'], cyanide= presentCyanide, exposedtogasamine= exposureAcid, exposedtosulphur= exposedSulfur, exposuretoamine= data['ExposureAmine'],
                                h2s= EnvironmentCH2S, h2sinwater= data['H2SContent'], hydrogen= processHydrogen, hydrofluoric= presentHF, materialexposedtoclint= materialExposedFluid, maxoperatingpressure= data['maxOP'],
                                maxoperatingtemperature= float(data['maxOT']), minoperatingpressure= float(data['minOP']), minoperatingtemperature= data['minOT'],criticalexposuretemperature= data['criticalTemp'], naohconcentration= data['NaOHConcentration'],
                                releasefluidpercenttoxic= float(data['ReleasePercentToxic']), waterph= float(data['PHWater']), h2spartialpressure= float(data['OpHydroPressure']))
            rwstream.save()

            rwexcor = RwExtcorTemperature(id= rwassessment, minus12tominus8= data['OP1'], minus8toplus6= data['OP2'], plus6toplus32= data['OP3'], plus32toplus71= data['OP4'], plus71toplus107= data['OP5'],
                                          plus107toplus121= data['OP6'], plus121toplus135= data['OP7'], plus135toplus162= data['OP8'], plus162toplus176= data['OP9'], morethanplus176= data['OP10'])
            rwexcor.save()

            rwcoat = RwCoating(id= rwassessment, externalcoating= ExternalCoating, externalinsulation= ExternalInsulation, internalcladding= InternalCladding, internalcoating= InternalCoating, internallining= InternalLining,
                               externalcoatingdate= data['ExternalCoatingID'],externalcoatingquality= data['ExternalCoatingQuality'], externalinsulationtype= data['ExternalInsulationType'], insulationcondition= data['InsulationCondition'],
                               insulationcontainschloride= InsulationCholride, internallinercondition= data['InternalLinerCondition'],internallinertype = data['InternalLinerType'],claddingcorrosionrate= data['CladdingCorrosionRate'], supportconfignotallowcoatingmaint= supportMaterial)
            rwcoat.save()


            rwmaterial = RwMaterial(id = rwassessment, corrosionallowance=data['CA'],materialname= data['material'],designpressure= data['designPressure'],designtemperature= data['maxDesignTemp'], mindesigntemperature= data['minDesignTemp'],
                                    brittlefracturethickness= data['BrittleFacture'], sigmaphase= data['sigmaPhase'], sulfurcontent= data['sulfurContent'], heattreatment= data['heatTreatment'], referencetemperature= data['tempRef'],
                                    ptamaterialcode= data['PTAMaterialGrade'], hthamaterialcode= data['HTHAMaterialGrade'], ispta= materialPTA, ishtha= materialHTHA, austenitic= austeniticStell, temper= suscepTemp, carbonlowalloy= cacbonAlloy,
                                    nickelbased= nickelAlloy, chromemoreequal12= chromium, allowablestress= data['allowStress'], costfactor= data['materialCostFactor'])
            rwmaterial.save()

            rwinputca = RwInputCaLevel1(id= rwassessment, api_fluid= data['APIFluid'], system= data['Systerm'], release_duration= data['ReleaseDuration'], detection_type= data['DetectionType'], isulation_type= data['IsulationType'], mitigation_system= data['MittigationSysterm'],
                                        equipment_cost= data['EnvironmentCost'], injure_cost= data['InjureCost'], evironment_cost= data['EnvironmentCost'], toxic_percent= data['ToxicPercent'], personal_density= data['PersonDensity'],material_cost= data['materialCostFactor'],
                                        production_cost= data['ProductionCost'], mass_inventory= data['MassInventory'], mass_component= data['MassComponent'],stored_pressure= float(data['minOP'])*6.895,stored_temp= data['minOT'])
            rwinputca.save()

            if data['ExternalCoatingID'] is None:
                dm_cal = DM_CAL(ComponentNumber=str(dataCom.componentnumber), Commissiondate=dataEq.commissiondate,
                                AssessmentDate=datetime.strptime(str(rwassessment.assessmentdate), "%Y-%M-%d"),
                                APIComponentType=str(data['apicomponenttypeid']),
                                Diametter=float(data['normaldiameter']), NomalThick=float(data['normalthick']),
                                CurrentThick=float(data['currentthick']), MinThickReq=float(data['tmin']),
                                CorrosionRate=float(data['currentrate']), CA=float(data['CA']),
                                ProtectedBarrier=False, CladdingCorrosionRate=float(data['CladdingCorrosionRate']),
                                InternalCladding=bool(InternalCladding),
                                OnlineMonitoring=data['OnlineMonitoring'], HighlyEffectDeadleg=bool(HighlyEffe),
                                ContainsDeadlegs=bool(containsDeadlegs),
                                TankMaintain653=False, AdjustmentSettle="", ComponentIsWeld=False,
                                LinningType=data['InternalLinerType'], LINNER_ONLINE=bool(linerOnlineMoniter),
                                LINNER_CONDITION=data['InternalLinerCondition'], YEAR_IN_SERVICE=0,
                                INTERNAL_LINNING=bool(InternalLining),
                                HEAT_TREATMENT=data['heatTreatment'],
                                NaOHConcentration=float(data['NaOHConcentration']), HEAT_TRACE=bool(heatTrace),
                                STEAM_OUT=bool(steamOut),
                                AMINE_EXPOSED=bool(exposureAcid), AMINE_SOLUTION=data['AminSolution'],
                                ENVIRONMENT_H2S_CONTENT=bool(EnvironmentCH2S), AQUEOUS_OPERATOR=bool(aquaDuringOP),
                                AQUEOUS_SHUTDOWN=bool(aquaDuringShutdown),
                                H2SContent=float(data['H2SContent']), PH=float(data['PHWater']),
                                PRESENT_CYANIDE=bool(presentCyanide), BRINNEL_HARDNESS=data['MaxBrinell'],
                                SULFUR_CONTENT=data['sulfurContent'],
                                CO3_CONTENT=float(data['CO3']),
                                PTA_SUSCEP=bool(materialPTA), NICKEL_ALLOY=bool(nickelAlloy),
                                EXPOSED_SULFUR=bool(exposedSulfur),
                                ExposedSH2OOperation=bool(presentSulphide),
                                ExposedSH2OShutdown=bool(presentSulphidesShutdown),
                                ThermalHistory=data['ThermalHistory'], PTAMaterial=data['PTAMaterialGrade'],
                                DOWNTIME_PROTECTED=bool(downtime),
                                INTERNAL_EXPOSED_FLUID_MIST=bool(materialExposedFluid),
                                EXTERNAL_EXPOSED_FLUID_MIST=bool(materialExposed),
                                CHLORIDE_ION_CONTENT=float(data['ChlorideIon']),
                                HF_PRESENT=bool(presentHF),
                                INTERFACE_SOIL_WATER=bool(interfaceSoilWater), SUPPORT_COATING=bool(supportMaterial),
                                INSULATION_TYPE=data['ExternalInsulationType'],
                                CUI_PERCENT_1=data['OP1'], CUI_PERCENT_2=data['OP2'],
                                CUI_PERCENT_3=data['OP3'], CUI_PERCENT_4=data['OP4'], CUI_PERCENT_5=data['OP5'],
                                CUI_PERCENT_6=data['OP6'], CUI_PERCENT_7=data['OP7'], CUI_PERCENT_8=data['OP8'],
                                CUI_PERCENT_9=data['OP9'], CUI_PERCENT_10=data['OP10'],
                                EXTERNAL_INSULATION=bool(ExternalInsulation),
                                COMPONENT_INSTALL_DATE= dataEq.commissiondate,
                                CRACK_PRESENT=bool(crackpresent),
                                EXTERNAL_EVIRONMENT=data['ExternalEnvironment'],
                                EXTERN_COAT_QUALITY=data['ExternalCoatingQuality'],
                                PIPING_COMPLEXITY=data['complex'], INSULATION_CONDITION=data['InsulationCondition'],
                                INSULATION_CHLORIDE=bool(InsulationCholride),
                                MATERIAL_SUSCEP_HTHA=bool(materialHTHA), HTHA_MATERIAL=data['HTHAMaterialGrade'],
                                HTHA_PRESSURE=float(data['OpHydroPressure']) * 0.006895,
                                CRITICAL_TEMP=float(data['criticalTemp']), DAMAGE_FOUND=bool(damageDuringInsp),
                                LOWEST_TEMP=bool(lowestTemp),
                                TEMPER_SUSCEP=bool(suscepTemp), PWHT=bool(pwht),
                                BRITTLE_THICK=float(data['BrittleFacture']), CARBON_ALLOY=bool(cacbonAlloy),
                                DELTA_FATT=float(data['deltafatt']),
                                MAX_OP_TEMP=float(data['maxOT']), CHROMIUM_12=bool(chromium),
                                MIN_OP_TEMP=float(data['minOT']), MIN_DESIGN_TEMP=float(data['minDesignTemp']),
                                REF_TEMP=float(data['tempRef']),
                                AUSTENITIC_STEEL=bool(austeniticStell), PERCENT_SIGMA=float(data['sigmaPhase']),
                                EquipmentType=data['equipmentType'], PREVIOUS_FAIL=data['prevFailure'],
                                AMOUNT_SHAKING=data['shakingPipe'], TIME_SHAKING=data['timeShakingPipe'],
                                CYLIC_LOAD=data['CylicLoad'],
                                CORRECT_ACTION=data['correctActionMitigate'], NUM_PIPE=data['numberPipe'],
                                PIPE_CONDITION=data['pipeCondition'], JOINT_TYPE=data['joinTypeBranch'],
                                BRANCH_DIAMETER=data['branchDiameter'])
            else:
                dm_cal = DM_CAL(ComponentNumber=str(dataCom.componentnumber), Commissiondate=dataEq.commissiondate,
                                AssessmentDate=datetime.strptime(str(rwassessment.assessmentdate), "%Y-%M-%d"),
                                APIComponentType=str(data['apicomponenttypeid']),
                                Diametter=float(data['normaldiameter']), NomalThick=float(data['normalthick']),
                                CurrentThick=float(data['currentthick']), MinThickReq=float(data['tmin']),
                                CorrosionRate=float(data['currentrate']), CA=float(data['CA']),
                                ProtectedBarrier=False, CladdingCorrosionRate=float(data['CladdingCorrosionRate']),
                                InternalCladding=bool(InternalCladding),
                                OnlineMonitoring=data['OnlineMonitoring'], HighlyEffectDeadleg=bool(HighlyEffe),
                                ContainsDeadlegs=bool(containsDeadlegs),
                                TankMaintain653=False, AdjustmentSettle="", ComponentIsWeld=False,
                                LinningType=data['InternalLinerType'], LINNER_ONLINE=bool(linerOnlineMoniter),
                                LINNER_CONDITION=data['InternalLinerCondition'], YEAR_IN_SERVICE=0,
                                INTERNAL_LINNING=bool(InternalLining),
                                HEAT_TREATMENT=data['heatTreatment'],
                                NaOHConcentration=float(data['NaOHConcentration']), HEAT_TRACE=bool(heatTrace),
                                STEAM_OUT=bool(steamOut),
                                AMINE_EXPOSED=bool(exposureAcid), AMINE_SOLUTION=data['AminSolution'],
                                ENVIRONMENT_H2S_CONTENT=bool(EnvironmentCH2S), AQUEOUS_OPERATOR=bool(aquaDuringOP),
                                AQUEOUS_SHUTDOWN=bool(aquaDuringShutdown),
                                H2SContent=float(data['H2SContent']), PH=float(data['PHWater']),
                                PRESENT_CYANIDE=bool(presentCyanide), BRINNEL_HARDNESS=data['MaxBrinell'],
                                SULFUR_CONTENT=data['sulfurContent'],
                                CO3_CONTENT=float(data['CO3']),
                                PTA_SUSCEP=bool(materialPTA), NICKEL_ALLOY=bool(nickelAlloy),
                                EXPOSED_SULFUR=bool(exposedSulfur),
                                ExposedSH2OOperation=bool(presentSulphide),
                                ExposedSH2OShutdown=bool(presentSulphidesShutdown),
                                ThermalHistory=data['ThermalHistory'], PTAMaterial=data['PTAMaterialGrade'],
                                DOWNTIME_PROTECTED=bool(downtime),
                                INTERNAL_EXPOSED_FLUID_MIST=bool(materialExposedFluid),
                                EXTERNAL_EXPOSED_FLUID_MIST=bool(materialExposed),
                                CHLORIDE_ION_CONTENT=float(data['ChlorideIon']),
                                HF_PRESENT=bool(presentHF),
                                INTERFACE_SOIL_WATER=bool(interfaceSoilWater), SUPPORT_COATING=bool(supportMaterial),
                                INSULATION_TYPE=data['ExternalInsulationType'],
                                CUI_PERCENT_1=data['OP1'], CUI_PERCENT_2=data['OP2'],
                                CUI_PERCENT_3=data['OP3'], CUI_PERCENT_4=data['OP4'], CUI_PERCENT_5=data['OP5'],
                                CUI_PERCENT_6=data['OP6'], CUI_PERCENT_7=data['OP7'], CUI_PERCENT_8=data['OP8'],
                                CUI_PERCENT_9=data['OP9'], CUI_PERCENT_10=data['OP10'],
                                EXTERNAL_INSULATION=bool(ExternalInsulation),
                                COMPONENT_INSTALL_DATE=datetime.strptime(str(data['ExternalCoatingID']), "%Y-%M-%d"),
                                CRACK_PRESENT=bool(crackpresent),
                                EXTERNAL_EVIRONMENT=data['ExternalEnvironment'],
                                EXTERN_COAT_QUALITY=data['ExternalCoatingQuality'],
                                PIPING_COMPLEXITY=data['complex'], INSULATION_CONDITION=data['InsulationCondition'],
                                INSULATION_CHLORIDE=bool(InsulationCholride),
                                MATERIAL_SUSCEP_HTHA=bool(materialHTHA), HTHA_MATERIAL=data['HTHAMaterialGrade'],
                                HTHA_PRESSURE=float(data['OpHydroPressure']) * 0.006895,
                                CRITICAL_TEMP=float(data['criticalTemp']), DAMAGE_FOUND=bool(damageDuringInsp),
                                LOWEST_TEMP=bool(lowestTemp),
                                TEMPER_SUSCEP=bool(suscepTemp), PWHT=bool(pwht),
                                BRITTLE_THICK=float(data['BrittleFacture']), CARBON_ALLOY=bool(cacbonAlloy),
                                DELTA_FATT=float(data['deltafatt']),
                                MAX_OP_TEMP=float(data['maxOT']), CHROMIUM_12=bool(chromium),
                                MIN_OP_TEMP=float(data['minOT']), MIN_DESIGN_TEMP=float(data['minDesignTemp']),
                                REF_TEMP=float(data['tempRef']),
                                AUSTENITIC_STEEL=bool(austeniticStell), PERCENT_SIGMA=float(data['sigmaPhase']),
                                EquipmentType=data['equipmentType'], PREVIOUS_FAIL=data['prevFailure'],
                                AMOUNT_SHAKING=data['shakingPipe'], TIME_SHAKING=data['timeShakingPipe'],
                                CYLIC_LOAD=data['CylicLoad'],
                                CORRECT_ACTION=data['correctActionMitigate'], NUM_PIPE=data['numberPipe'],
                                PIPE_CONDITION=data['pipeCondition'], JOINT_TYPE=data['joinTypeBranch'],
                                BRANCH_DIAMETER=data['branchDiameter'])
            ca_cal = CA_NORMAL(NominalDiametter = float(data['normaldiameter']), MATERIAL_COST = float(data['materialCostFactor']), FLUID = data['APIFluid'], FLUID_PHASE = data['Systerm'], API_COMPONENT_TYPE_NAME =data['apicomponenttypeid'] , DETECTION_TYPE = data['DetectionType'],
                 ISULATION_TYPE = data['IsulationType'], STORED_PRESSURE = float(data['minOP'])*6.895, ATMOSPHERIC_PRESSURE = 101, STORED_TEMP = float(data['minOT']) + 273, MASS_INVERT = float(data['MassInventory']),
                 MASS_COMPONENT = float(data['MassComponent']), MITIGATION_SYSTEM = data['MittigationSysterm'], TOXIC_PERCENT = float(data['ToxicPercent']), RELEASE_DURATION = data['ReleaseDuration'], PRODUCTION_COST = float(data['ProductionCost']),
                 INJURE_COST = float(data['InjureCost']), ENVIRON_COST = float(data['EnvironmentCost']), PERSON_DENSITY = float(data['PersonDensity']), EQUIPMENT_COST = float(data['EquipmentCost']))


            TOTAL_DF_API1 = dm_cal.DF_TOTAL_API(0)
            TOTAL_DF_API2 = dm_cal.DF_TOTAL_API(3)
            TOTAL_DF_API3 = dm_cal.DF_TOTAL_API(6)
            gffTotal = api.gfftotal
            pofap1 = TOTAL_DF_API1 * dataFaci.managementfactor * gffTotal
            pofap2 = TOTAL_DF_API2 * dataFaci.managementfactor * gffTotal
            pofap3 = TOTAL_DF_API3 * dataFaci.managementfactor * gffTotal

            # thinningtype = General or Local
            refullPOF = RwFullPof(id= rwassessment, thinningap1= dm_cal.DF_THINNING_TOTAL_API(0), thinningap2= dm_cal.DF_THINNING_TOTAL_API(3) , thinningap3= dm_cal.DF_THINNING_TOTAL_API(6),
                                  sccap1= dm_cal.DF_SSC_TOTAL_API(0), sccap2= dm_cal.DF_SSC_TOTAL_API(3), sccap3= dm_cal.DF_SSC_TOTAL_API(6),
                                  externalap1= dm_cal.DF_EXT_TOTAL_API(0), externalap2= dm_cal.DF_EXT_TOTAL_API(3),externalap3= dm_cal.DF_EXT_TOTAL_API(6),
                                  brittleap1=dm_cal.DF_BRIT_TOTAL_API(), brittleap2= dm_cal.DF_BRIT_TOTAL_API(), brittleap3= dm_cal.DF_BRIT_TOTAL_API(),
                                  htha_ap1= dm_cal.DF_HTHA_API(0), htha_ap2= dm_cal.DF_HTHA_API(3), htha_ap3= dm_cal.DF_HTHA_API(6),
                                  fatigueap1= dm_cal.DF_PIPE_API(), fatigueap2= dm_cal.DF_PIPE_API(), fatigueap3= dm_cal.DF_PIPE_API(),
                                  fms= dataFaci.managementfactor, thinningtype="Local",
                                  thinninglocalap1= max(dm_cal.DF_THINNING_TOTAL_API(0), dm_cal.DF_EXT_TOTAL_API(0)), thinninglocalap2= max(dm_cal.DF_THINNING_TOTAL_API(3), dm_cal.DF_EXT_TOTAL_API(3)), thinninglocalap3= max(dm_cal.DF_THINNING_TOTAL_API(6), dm_cal.DF_EXT_TOTAL_API(6)),
                                  thinninggeneralap1= dm_cal.DF_THINNING_TOTAL_API(0) + dm_cal.DF_EXT_TOTAL_API(0), thinninggeneralap2= dm_cal.DF_THINNING_TOTAL_API(3) + dm_cal.DF_EXT_TOTAL_API(3), thinninggeneralap3= dm_cal.DF_THINNING_TOTAL_API(6) + dm_cal.DF_EXT_TOTAL_API(6),
                                  totaldfap1= TOTAL_DF_API1, totaldfap2= TOTAL_DF_API2, totaldfap3= TOTAL_DF_API3,
                                  pofap1= pofap1, pofap2= pofap2, pofap3= pofap3,gfftotal= gffTotal,
                                  pofap1category= dm_cal.PoFCategory(TOTAL_DF_API1), pofap2category= dm_cal.PoFCategory(TOTAL_DF_API2), pofap3category= dm_cal.PoFCategory(TOTAL_DF_API3))

            refullPOF.save()

            if ca_cal.NominalDiametter == 0 or ca_cal.STORED_PRESSURE == 0 or ca_cal.MASS_INVERT == 0 or ca_cal.MASS_COMPONENT == 0:
                calv1 = RwCaLevel1(id= rwassessment,release_phase= ca_cal.GET_RELEASE_PHASE(),fact_di= ca_cal.fact_di(),
                                   fact_mit=ca_cal.fact_mit(), fact_ait=ca_cal.fact_ait(),fc_total= 100000000,fcof_category="E" )
            else:
                calv1 = RwCaLevel1(id= rwassessment, release_phase= ca_cal.GET_RELEASE_PHASE(), fact_di= ca_cal.fact_di(), ca_inj_flame= ca_cal.ca_inj_flame(),
                                   ca_inj_toxic= ca_cal.ca_inj_tox(), ca_inj_ntnf= ca_cal.ca_inj_nfnt(),
                                   fact_mit= ca_cal.fact_mit(), fact_ait= ca_cal.fact_ait(), ca_cmd= ca_cal.ca_cmd(), fc_cmd= ca_cal.fc_cmd(),
                                   fc_affa= ca_cal.fc_affa(), fc_envi= ca_cal.fc_environ(), fc_prod= ca_cal.fc_prod(), fc_inj= ca_cal.fc_inj(),
                                   fc_total= ca_cal.fc(), fcof_category= ca_cal.FC_Category(ca_cal.fc()))

            calv1.save()
            # damage machinsm
            damageList = dm_cal.ISDF()
            for damage in damageList:
                damageMachinsm = RwDamageMechanism(id_dm=rwassessment, dmitemid_id= damage['DM_ITEM_ID'],
                                                   isactive=damage['isActive'],
                                                   df1=damage['DF1'], df2=damage['DF2'], df3=damage['DF3'],
                                                   highestinspectioneffectiveness=damage['highestEFF'],
                                                   secondinspectioneffectiveness=damage['secondEFF'],
                                                   numberofinspections=damage['numberINSP'],
                                                   lastinspdate=damage['lastINSP'].date().strftime('%Y-%m-%d'),
                                                   inspduedate= dm_cal.INSP_DUE_DATE(ca_cal.fc(), gffTotal, dataFaci.managementfactor, dataFaciTarget.risktarget_fc).date().strftime('%Y-%m-%d'))
                damageMachinsm.save()

            refullfc = RwFullFcof(id=rwassessment,fcofvalue= calv1.fc_total, fcofcategory= calv1.fcof_category, envcost= data['EnvironmentCost'],
                                  equipcost= data['EquipmentCost'], prodcost= data['ProductionCost'], popdens= data['PersonDensity'], injcost= data['InjureCost'])
            refullfc.save()

            return redirect('resultca', rwassessment.id)
    except ComponentMaster.DoesNotExist:
        raise Http404
    return render(request, 'home/new/Normal.html',{'facility': dataFaci,'component': dataCom , 'equipment':dataEq,'api':api,'commissiondate': commisiondate,'dataLink': data['islink'], 'fluid': Fluid})

def newProposalTank(request, componentname):
    try:
        dataCom = ComponentMaster.objects.get(componentid= componentname)
        dataEq = EquipmentMaster.objects.get(equipmentid=dataCom.equipmentid_id)
        dataFaci = Facility.objects.get(facilityid=dataEq.facilityid_id)
        dataFaciTarget = FacilityRiskTarget.objects.get(facilityid= dataEq.facilityid_id)
        api = ApiComponentType.objects.get(apicomponenttypeid=dataCom.apicomponenttypeid)
        data = {}
        data['islink'] = dataCom.isequipmentlinked
        commisiondate = dataEq.commissiondate.date().strftime('%Y-%m-%d')
        #shell = ["COURSE-1", "COURSE-2", "COURSE-3", "COURSE-4", "COURSE-5", "COURSE-6", "COURSE-7", "COURSE-8",
        #         "COURSE-9", "COURSE-10"]
        checkshell = False
        if dataCom.componenttypeid_id == 8 or dataCom.componenttypeid_id == 38:
            checkshell = True

        if request.method =="POST":
            # Data Assessment
            data['assessmentName'] = request.POST.get('AssessmentName')
            data['assessmentdate'] = request.POST.get('assessmentdate')
            data['riskperiod'] = request.POST.get('RiskAnalysisPeriod')
            data['apicomponenttypeid'] = api.apicomponenttypename

            # Data Equipment Properties
            if request.POST.get('Admin'):
                adminControlUpset = 1
            else:
                adminControlUpset = 0

            if request.POST.get('CylicOper'):
                cylicOp = 1
            else:
                cylicOp = 0

            if request.POST.get('Highly'):
                highlyDeadleg = 1
            else:
                highlyDeadleg = 0

            if request.POST.get('Steamed'):
                steamOutWater = 1
            else:
                steamOutWater = 0

            if request.POST.get('Downtime'):
                downtimeProtect = 1
            else:
                downtimeProtect = 0

            if request.POST.get('PWHT'):
                pwht = 1
            else:
                pwht = 0

            if request.POST.get('HeatTraced'):
                heatTrace = 1
            else:
                heatTrace = 0

            data['distance'] = request.POST.get('Distance')

            if request.POST.get('InterfaceSoilWater'):
                interfaceSoilWater = 1
            else:
                interfaceSoilWater = 0

            data['soiltype'] = request.POST.get('typeofSoil')

            if request.POST.get('PressurisationControlled'):
                pressureControl = 1
            else:
                pressureControl = 0

            data['minRequireTemp'] = request.POST.get('MinReq')

            if request.POST.get('lowestTemp'):
                lowestTemp = 1
            else:
                lowestTemp = 0

            if request.POST.get('MFTF'):
                materialChlorineExt = 1
            else:
                materialChlorineExt = 0

            if request.POST.get('LOM'):
                linerOnlineMonitor = 1
            else:
                linerOnlineMonitor = 0

            if request.POST.get('PresenceofSulphides'):
                presenceSulphideOP = 1
            else:
                presenceSulphideOP = 0

            if request.POST.get('PresenceofSulphidesShutdow'):
                presenceSulphideShut = 1
            else:
                presenceSulphideShut = 0

            if request.POST.get('ComponentWelded'):
                componentWelded = 1
            else:
                componentWelded = 0

            if request.POST.get('TMA'):
                tankIsMaintain = 1
            else:
                tankIsMaintain = 0

            data['adjustSettlement'] = request.POST.get('AdjForSettlement')
            data['extEnvironment'] = request.POST.get('ExternalEnvironment')
            data['EnvSensitivity'] = request.POST.get('EnvironmentSensitivity')
            data['themalHistory'] = request.POST.get('ThermalHistory')
            data['onlineMonitor'] = request.POST.get('OnlineMonitoring')
            data['equipmentVolumn'] = request.POST.get('EquipmentVolume')

            #Component Properties
            data['tankDiameter'] = request.POST.get('TankDiameter')
            data['NominalThickness'] = request.POST.get('NominalThickness')
            data['currentThick'] = request.POST.get('CurrentThickness')
            data['minRequireThick'] = request.POST.get('MinReqThick')
            data['currentCorrosion'] = request.POST.get('CurrentCorrosionRate')
            data['shellHieght'] = request.POST.get('shellHeight')

            if request.POST.get('DFDI'):
                damageFound = 1
            else:
                damageFound = 0

            if request.POST.get('PresenceCracks'):
                crackPresence = 1
            else:
                crackPresence = 0

            if request.POST.get('TrampElements'):
                trampElements = 1
            else:
                trampElements = 0

            if request.POST.get('ReleasePreventionBarrier'):
                preventBarrier = 1
            else:
                preventBarrier = 0

            if request.POST.get('ConcreteFoundation'):
                concreteFoundation = 1
            else:
                concreteFoundation = 0

            data['maxBrinnelHardness'] = request.POST.get('MBHW')
            data['complexProtrusion'] = request.POST.get('ComplexityProtrusions')
            data['severityVibration'] = request.POST.get('SeverityVibration')

            # Operating condition
            data['maxOT'] = request.POST.get('MaxOT')
            data['maxOP'] = request.POST.get('MaxOP')
            data['minOT'] = request.POST.get('MinOT')
            data['minOP'] = request.POST.get('MinOP')
            data['H2Spressure'] = request.POST.get('OHPP')
            data['flowRate'] = request.POST.get('FlowRate')
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

            # Material
            data['materialName'] = request.POST.get('materialname')
            data['maxDesignTemp'] = request.POST.get('MaxDesignTemp')
            data['minDesignTemp'] = request.POST.get('MinDesignTemp')
            data['designPressure'] = request.POST.get('DesignPressure')
            data['refTemp'] = request.POST.get('ReferenceTemperature')
            data['allowStress'] = request.POST.get('ASAT')
            data['brittleThick'] = request.POST.get('BFGT')
            data['corrosionAllow'] = request.POST.get('CorrosionAllowance')

            if request.POST.get('CoLAS'):
                carbonLowAlloySteel = 1
            else:
                carbonLowAlloySteel = 0

            if request.POST.get('AusteniticSteel'):
                austeniticSteel = 1
            else:
                austeniticSteel = 0

            if request.POST.get('NickelAlloy'):
                nickelAlloy = 1
            else:
                nickelAlloy = 0

            if request.POST.get('Chromium'):
                chromium = 1
            else:
                chromium = 0

            data['sulfurContent'] = request.POST.get('SulfurContent')
            data['heatTreatment'] = request.POST.get('heatTreatment')

            if request.POST.get('MGTEPTA'):
                materialPTA = 1
            else:
                materialPTA = 0

            data['PTAMaterialGrade'] = request.POST.get('PTAMaterialGrade')
            data['materialCostFactor'] = request.POST.get('MaterialCostFactor')
            data['productionCost'] = request.POST.get('ProductionCost')

            # Coating, Cladding
            if request.POST.get('InternalCoating'):
                internalCoating = 1
            else:
                internalCoating = 0

            if request.POST.get('ExternalCoating'):
                externalCoating = 1
            else:
                externalCoating = 0

            data['externalInstallDate'] = request.POST.get('ExternalCoatingID')
            data['externalCoatQuality'] = request.POST.get('ExternalCoatingQuality')

            if request.POST.get('SCWD'):
                supportCoatingMaintain = 1
            else:
                supportCoatingMaintain = 0

            if request.POST.get('InternalCladding'):
                internalCladding = 1
            else:
                internalCladding = 0

            data['cladCorrosion'] = request.POST.get('CladdingCorrosionRate')

            if request.POST.get('InternalLining'):
                internalLinning = 1
            else:
                internalLinning = 0

            data['internalLinnerType'] = request.POST.get('InternalLinerType')
            data['internalLinnerCondition'] = request.POST.get('InternalLinerCondition')

            if request.POST.get('ExternalInsulation'):
                extInsulation = 1
            else:
                extInsulation = 0

            if request.POST.get('ICC'):
                InsulationContainChloride = 1
            else:
                InsulationContainChloride = 0

            data['extInsulationType'] = request.POST.get('ExternalInsulationType')
            data['insulationCondition'] = request.POST.get('InsulationCondition')

            # Stream
            data['fluid'] = request.POST.get('Fluid')
            data['fluidHeight'] = request.POST.get('FluidHeight')
            data['fluidLeaveDike'] = request.POST.get('PFLD')
            data['fluidOnsite'] = request.POST.get('PFLDRS')
            data['fluidOffsite'] = request.POST.get('PFLDGoffsite')
            data['naohConcent'] = request.POST.get('NaOHConcentration')
            data['releasePercentToxic'] = request.POST.get('RFPT')
            data['chlorideIon'] = request.POST.get('ChlorideIon')
            data['co3'] = request.POST.get('CO3')
            data['h2sContent'] = request.POST.get('H2SContent')
            data['PHWater'] = request.POST.get('PHWater')

            if request.POST.get('EAGTA'):
                exposedAmine = 1
            else:
                exposedAmine = 0

            data['amineSolution'] = request.POST.get('AmineSolution')
            data['exposureAmine'] = request.POST.get('ExposureAmine')

            if request.POST.get('APDO'):
                aqueosOP = 1
            else:
                aqueosOP = 0

            if request.POST.get('EnvironmentCH2S'):
                environtH2S = 1
            else:
                environtH2S = 0

            if request.POST.get('APDSD'):
                aqueosShut = 1
            else:
                aqueosShut = 0

            if request.POST.get('PresenceCyanides'):
                cyanidesPresence = 1
            else:
                cyanidesPresence = 0

            if request.POST.get('presenceHF'):
                presentHF = 1
            else:
                presentHF = 0

            if request.POST.get('ECCAC'):
                environtCaustic = 1
            else:
                environtCaustic = 0

            if request.POST.get('PCH'):
                processContainHydro = 1
            else:
                processContainHydro = 0

            if request.POST.get('MEFMSCC'):
                materialChlorineIntern = 1
            else:
                materialChlorineIntern = 0

            if request.POST.get('ESBC'):
                exposedSulfur = 1
            else:
                exposedSulfur = 0

            if str(data['fluid']) == "Gasoline":
                apiFluid = "C6-C8"
            elif str(data['fluid']) == "Light Diesel Oil":
                apiFluid = "C9-C12"
            elif str(data['fluid']) == "Heavy Diesel Oil":
                apiFluid = "C13-C16"
            elif str(data['fluid']) == "Fuel Oil" or str(data['fluid']) == "Crude Oil":
                apiFluid = "C17-C25"
            else:
                apiFluid = "C25+"

            rwassessment = RwAssessment(equipmentid= dataEq, componentid= dataCom, assessmentdate= data['assessmentdate'], riskanalysisperiod= data['riskperiod'],
                                        isequipmentlinked= data['islink'], proposalname= data['assessmentName'])
            rwassessment.save()
            rwequipment = RwEquipment(id=rwassessment, commissiondate= commisiondate,
                                      adminupsetmanagement=adminControlUpset,
                                      cyclicoperation=cylicOp, highlydeadleginsp=highlyDeadleg,
                                      downtimeprotectionused=downtimeProtect,steamoutwaterflush=steamOutWater,
                                      pwht=pwht,heattraced=heatTrace,distancetogroundwater= data['distance'],
                                      interfacesoilwater=interfaceSoilWater, typeofsoil= data['soiltype'],
                                      pressurisationcontrolled=pressureControl,
                                      minreqtemperaturepressurisation=data['minRequireTemp'],yearlowestexptemp=lowestTemp,
                                      materialexposedtoclext=materialChlorineExt,lineronlinemonitoring=linerOnlineMonitor,
                                      presencesulphideso2=presenceSulphideOP,presencesulphideso2shutdown=presenceSulphideShut,
                                      componentiswelded= componentWelded, tankismaintained= tankIsMaintain,
                                      adjustmentsettle= data['adjustSettlement'],
                                      externalenvironment=data['extEnvironment'],
                                      environmentsensitivity= data['EnvSensitivity'],
                                      onlinemonitoring=data['onlineMonitor'],thermalhistory=data['themalHistory'],
                                      managementfactor=dataFaci.managementfactor,
                                      volume=data['equipmentVolumn'])
            rwequipment.save()

            rwcomponent = RwComponent(id=rwassessment, nominaldiameter=data['tankDiameter'],
                                      nominalthickness=data['NominalThickness'], currentthickness=data['currentThick'],
                                      minreqthickness=data['minRequireThick'], currentcorrosionrate=data['currentCorrosion'],
                                      shellheight= data['shellHieght'],damagefoundinspection= damageFound,
                                      crackspresent= crackPresence,trampelements= trampElements,
                                      releasepreventionbarrier= preventBarrier, concretefoundation= concreteFoundation,
                                      brinnelhardness= data['maxBrinnelHardness'],complexityprotrusion= data['complexProtrusion'],
                                      severityofvibration= data['severityVibration'])
            rwcomponent.save()

            rwstream = RwStream(id=rwassessment, maxoperatingtemperature= data['maxOT'], maxoperatingpressure= data['maxOP'],
                                minoperatingtemperature= data['minOT'], minoperatingpressure= data['minOP'],
                                h2spartialpressure= data['H2Spressure'], criticalexposuretemperature= data['criticalTemp'],
                                tankfluidname=data['fluid'], fluidheight= data['fluidHeight'], fluidleavedikepercent=data['fluidLeaveDike'],
                                fluidleavedikeremainonsitepercent= data['fluidOnsite'], fluidgooffsitepercent= data['fluidOffsite'],
                                naohconcentration= data['naohConcent'], releasefluidpercenttoxic= data['releasePercentToxic'],
                                chloride= data['chlorideIon'], co3concentration= data['co3'], h2sinwater= data['h2sContent'],
                                waterph= data['PHWater'], exposedtogasamine=exposedAmine, aminesolution= data['amineSolution'],
                                exposuretoamine= data['exposureAmine'], aqueousoperation= aqueosOP, h2s= environtH2S,
                                aqueousshutdown= aqueosShut, cyanide= cyanidesPresence, hydrofluoric= presentHF,
                                caustic= environtCaustic, hydrogen= processContainHydro, materialexposedtoclint= materialChlorineIntern,
                                exposedtosulphur= exposedSulfur)
            rwstream.save()

            rwexcor = RwExtcorTemperature(id=rwassessment, minus12tominus8=data['OP1'] , minus8toplus6=data['OP2'] ,
                                          plus6toplus32=data['OP3'], plus32toplus71=data['OP4'],
                                          plus71toplus107=data['OP5'],
                                          plus107toplus121=data['OP6'], plus121toplus135=data['OP7'],
                                          plus135toplus162=data['OP8'], plus162toplus176=data['OP9'],
                                          morethanplus176=data['OP10'])
            rwexcor.save()

            rwcoat = RwCoating(id=rwassessment, internalcoating= internalCoating, externalcoating= externalCoating,
                               externalcoatingdate= data['externalInstallDate'], externalcoatingquality= data['externalCoatQuality'],
                               supportconfignotallowcoatingmaint= supportCoatingMaintain, internalcladding= internalCladding,
                               claddingcorrosionrate= data['cladCorrosion'], internallining= internalLinning, internallinertype= data['internalLinnerType'],
                               internallinercondition= data['internalLinnerCondition'], externalinsulation= extInsulation, insulationcontainschloride= InsulationContainChloride,
                               externalinsulationtype= data['extInsulationType'], insulationcondition= data['insulationCondition']
                               )
            rwcoat.save()

            rwmaterial = RwMaterial(id=rwassessment, materialname= data['materialName'], designtemperature= data['maxDesignTemp'],
                                    mindesigntemperature= data['minDesignTemp'], designpressure= data['designPressure'], referencetemperature= data['refTemp'],
                                    allowablestress= data['allowStress'], brittlefracturethickness= data['brittleThick'], corrosionallowance= data['corrosionAllow'],
                                    carbonlowalloy= carbonLowAlloySteel, austenitic= austeniticSteel, nickelbased= nickelAlloy, chromemoreequal12= chromium,
                                    sulfurcontent= data['sulfurContent'], heattreatment= data['heatTreatment'], ispta= materialPTA, ptamaterialcode= data['PTAMaterialGrade'],
                                    costfactor= data['materialCostFactor'])
            rwmaterial.save()

            rwinputca = RwInputCaTank(id = rwassessment, fluid_height= data['fluidHeight'], shell_course_height= data['shellHieght'],
                                      tank_diametter= data['tankDiameter'], prevention_barrier= preventBarrier, environ_sensitivity= data['EnvSensitivity'],
                                      p_lvdike= data['fluidLeaveDike'], p_offsite= data['fluidOffsite'], p_onsite= data['fluidOnsite'], soil_type= data['soiltype'],
                                      tank_fluid= data['fluid'], api_fluid= apiFluid, sw= data['distance'], productioncost= data['productionCost'])
            rwinputca.save()

            if data['externalInstallDate'] is None:
                dm_cal = DM_CAL(APIComponentType= data['apicomponenttypeid'],
                                Diametter=float(data['tankDiameter']), NomalThick=float(data['NominalThickness']),
                                CurrentThick=float(rwcomponent.currentthickness),
                                MinThickReq=float(rwcomponent.minreqthickness),
                                CorrosionRate=float(rwcomponent.currentcorrosionrate),
                                CA=float(rwmaterial.corrosionallowance),
                                ProtectedBarrier=bool(rwcomponent.releasepreventionbarrier),
                                CladdingCorrosionRate=float(rwcoat.claddingcorrosionrate),
                                InternalCladding=bool(rwcoat.internalcladding), NoINSP_THINNING=1,
                                EFF_THIN="B", OnlineMonitoring=rwequipment.onlinemonitoring,
                                HighlyEffectDeadleg=bool(rwequipment.highlydeadleginsp),
                                ContainsDeadlegs=bool(rwequipment.containsdeadlegs),
                                TankMaintain653=bool(rwequipment.tankismaintained),
                                AdjustmentSettle=rwequipment.adjustmentsettle,
                                ComponentIsWeld=bool(rwequipment.componentiswelded),
                                LinningType=data['internalLinnerType'],
                                LINNER_ONLINE=bool(rwequipment.lineronlinemonitoring),
                                LINNER_CONDITION=data['internalLinnerCondition'],
                                INTERNAL_LINNING=bool(rwcoat.internallining),
                                HEAT_TREATMENT=data['heatTreatment'],
                                NaOHConcentration=float(data['naohConcent']), HEAT_TRACE=bool(heatTrace),
                                STEAM_OUT=bool(steamOutWater),
                                AMINE_EXPOSED=bool(exposedAmine),
                                AMINE_SOLUTION=data['amineSolution'],
                                ENVIRONMENT_H2S_CONTENT=bool(environtH2S), AQUEOUS_OPERATOR=bool(aqueosOP),
                                AQUEOUS_SHUTDOWN=bool(aqueosShut), H2SContent=float(data['h2sContent']),
                                PH=float(data['PHWater']),
                                PRESENT_CYANIDE=bool(cyanidesPresence), BRINNEL_HARDNESS=data['maxBrinnelHardness'],
                                SULFUR_CONTENT=data['sulfurContent'],
                                CO3_CONTENT=float(data['co3']),
                                PTA_SUSCEP=bool(materialPTA), NICKEL_ALLOY=bool(nickelAlloy),
                                EXPOSED_SULFUR=bool(exposedSulfur),
                                ExposedSH2OOperation=bool(presenceSulphideOP),
                                ExposedSH2OShutdown=bool(presenceSulphideShut), ThermalHistory=data['themalHistory'],
                                PTAMaterial=data['PTAMaterialGrade'],
                                DOWNTIME_PROTECTED=bool(downtimeProtect),
                                INTERNAL_EXPOSED_FLUID_MIST=bool(materialChlorineIntern),
                                EXTERNAL_EXPOSED_FLUID_MIST=bool(materialChlorineExt),
                                CHLORIDE_ION_CONTENT=float(data['chlorideIon']),
                                HF_PRESENT=bool(presentHF),
                                INTERFACE_SOIL_WATER=bool(interfaceSoilWater),
                                SUPPORT_COATING=bool(supportCoatingMaintain),
                                INSULATION_TYPE=data['extInsulationType'], CUI_PERCENT_1=float(data['OP1']),
                                CUI_PERCENT_2=float(data['OP2']),
                                CUI_PERCENT_3=float(data['OP3']), CUI_PERCENT_4=float(data['OP4']),
                                CUI_PERCENT_5=float(data['OP5']),
                                CUI_PERCENT_6=float(data['OP6']), CUI_PERCENT_7=float(data['OP7']),
                                CUI_PERCENT_8=float(data['OP8']),
                                CUI_PERCENT_9=float(data['OP9']), CUI_PERCENT_10=float(data['OP10']),
                                EXTERNAL_INSULATION=bool(extInsulation),
                                COMPONENT_INSTALL_DATE= dataEq.commissiondate,
                                CRACK_PRESENT=bool(crackPresence),
                                EXTERNAL_EVIRONMENT=data['extEnvironment'],
                                EXTERN_COAT_QUALITY=data['externalCoatQuality'],
                                PIPING_COMPLEXITY=data['complexProtrusion'],
                                INSULATION_CONDITION=data['insulationCondition'],
                                INSULATION_CHLORIDE=bool(InsulationContainChloride),
                                MATERIAL_SUSCEP_HTHA=False, HTHA_MATERIAL="",
                                HTHA_PRESSURE=float(data['H2Spressure']) * 0.006895,
                                CRITICAL_TEMP=float(data['criticalTemp']), DAMAGE_FOUND=bool(damageFound),
                                LOWEST_TEMP=bool(lowestTemp),
                                TEMPER_SUSCEP=False, PWHT=bool(pwht),
                                BRITTLE_THICK=float(data['brittleThick']), CARBON_ALLOY=bool(carbonLowAlloySteel),
                                DELTA_FATT=0,
                                MAX_OP_TEMP=float(data['maxOT']), CHROMIUM_12=bool(chromium),
                                MIN_OP_TEMP=float(data['minOT']), MIN_DESIGN_TEMP=float(data['minDesignTemp']),
                                REF_TEMP=float(data['refTemp']),
                                AUSTENITIC_STEEL=bool(austeniticSteel), PERCENT_SIGMA=0,
                                EquipmentType=dataEq.equipmenttypeid, PREVIOUS_FAIL="",
                                AMOUNT_SHAKING="", TIME_SHAKING="",
                                CYLIC_LOAD="",
                                CORRECT_ACTION="", NUM_PIPE="",
                                PIPE_CONDITION="", JOINT_TYPE="",
                                BRANCH_DIAMETER="")
            else:
                dm_cal = DM_CAL(APIComponentType= data['apicomponenttypeid'],
                                Diametter=float(data['tankDiameter']), NomalThick=float(data['NominalThickness']),
                                CurrentThick=float(rwcomponent.currentthickness),
                                MinThickReq=float(rwcomponent.minreqthickness),
                                CorrosionRate=float(rwcomponent.currentcorrosionrate),
                                CA=float(rwmaterial.corrosionallowance),
                                ProtectedBarrier=bool(rwcomponent.releasepreventionbarrier),
                                CladdingCorrosionRate=float(rwcoat.claddingcorrosionrate),
                                InternalCladding=bool(rwcoat.internalcladding), NoINSP_THINNING=1,
                                EFF_THIN="B", OnlineMonitoring=rwequipment.onlinemonitoring,
                                HighlyEffectDeadleg=bool(rwequipment.highlydeadleginsp),
                                ContainsDeadlegs=bool(rwequipment.containsdeadlegs),
                                TankMaintain653=bool(rwequipment.tankismaintained),
                                AdjustmentSettle=rwequipment.adjustmentsettle,
                                ComponentIsWeld=bool(rwequipment.componentiswelded),
                                LinningType=data['internalLinnerType'],
                                LINNER_ONLINE=bool(rwequipment.lineronlinemonitoring),
                                LINNER_CONDITION=data['internalLinnerCondition'],
                                INTERNAL_LINNING=bool(rwcoat.internallining),
                                HEAT_TREATMENT=data['heatTreatment'],
                                NaOHConcentration=float(data['naohConcent']), HEAT_TRACE=bool(heatTrace),
                                STEAM_OUT=bool(steamOutWater),
                                AMINE_EXPOSED=bool(exposedAmine),
                                AMINE_SOLUTION=data['amineSolution'],
                                ENVIRONMENT_H2S_CONTENT=bool(environtH2S), AQUEOUS_OPERATOR=bool(aqueosOP),
                                AQUEOUS_SHUTDOWN=bool(aqueosShut), H2SContent=float(data['h2sContent']),
                                PH=float(data['PHWater']),
                                PRESENT_CYANIDE=bool(cyanidesPresence), BRINNEL_HARDNESS=data['maxBrinnelHardness'],
                                SULFUR_CONTENT=data['sulfurContent'],
                                CO3_CONTENT=float(data['co3']),
                                PTA_SUSCEP=bool(materialPTA), NICKEL_ALLOY=bool(nickelAlloy),
                                EXPOSED_SULFUR=bool(exposedSulfur),
                                ExposedSH2OOperation=bool(presenceSulphideOP),
                                ExposedSH2OShutdown=bool(presenceSulphideShut), ThermalHistory=data['themalHistory'],
                                PTAMaterial=data['PTAMaterialGrade'],
                                DOWNTIME_PROTECTED=bool(downtimeProtect),
                                INTERNAL_EXPOSED_FLUID_MIST=bool(materialChlorineIntern),
                                EXTERNAL_EXPOSED_FLUID_MIST=bool(materialChlorineExt),
                                CHLORIDE_ION_CONTENT=float(data['chlorideIon']),
                                HF_PRESENT=bool(presentHF),
                                INTERFACE_SOIL_WATER=bool(interfaceSoilWater),
                                SUPPORT_COATING=bool(supportCoatingMaintain),
                                INSULATION_TYPE=data['extInsulationType'], CUI_PERCENT_1=float(data['OP1']),
                                CUI_PERCENT_2=float(data['OP2']),
                                CUI_PERCENT_3=float(data['OP3']), CUI_PERCENT_4=float(data['OP4']),
                                CUI_PERCENT_5=float(data['OP5']),
                                CUI_PERCENT_6=float(data['OP6']), CUI_PERCENT_7=float(data['OP7']),
                                CUI_PERCENT_8=float(data['OP8']),
                                CUI_PERCENT_9=float(data['OP9']), CUI_PERCENT_10=float(data['OP10']),
                                EXTERNAL_INSULATION=bool(extInsulation),
                                COMPONENT_INSTALL_DATE=datetime.strptime(str(data['externalInstallDate']), "%Y-%M-%d"),
                                CRACK_PRESENT=bool(crackPresence),
                                EXTERNAL_EVIRONMENT=data['extEnvironment'],
                                EXTERN_COAT_QUALITY=data['externalCoatQuality'],
                                PIPING_COMPLEXITY=data['complexProtrusion'],
                                INSULATION_CONDITION=data['insulationCondition'],
                                INSULATION_CHLORIDE=bool(InsulationContainChloride),
                                MATERIAL_SUSCEP_HTHA=False, HTHA_MATERIAL="",
                                HTHA_PRESSURE=float(data['H2Spressure']) * 0.006895,
                                CRITICAL_TEMP=float(data['criticalTemp']), DAMAGE_FOUND=bool(damageFound),
                                LOWEST_TEMP=bool(lowestTemp),
                                TEMPER_SUSCEP=False, PWHT=bool(pwht),
                                BRITTLE_THICK=float(data['brittleThick']), CARBON_ALLOY=bool(carbonLowAlloySteel),
                                DELTA_FATT=0,
                                MAX_OP_TEMP=float(data['maxOT']), CHROMIUM_12=bool(chromium),
                                MIN_OP_TEMP=float(data['minOT']), MIN_DESIGN_TEMP=float(data['minDesignTemp']),
                                REF_TEMP=float(data['refTemp']),
                                AUSTENITIC_STEEL=bool(austeniticSteel), PERCENT_SIGMA=0,
                                EquipmentType=dataEq.equipmenttypeid, PREVIOUS_FAIL="",
                                AMOUNT_SHAKING="", TIME_SHAKING="",
                                CYLIC_LOAD="",
                                CORRECT_ACTION="", NUM_PIPE="",
                                PIPE_CONDITION="", JOINT_TYPE="",
                                BRANCH_DIAMETER="")

            if checkshell:
                cacal = CA_SHELL(FLUID= apiFluid, FLUID_HEIGHT= float(data['fluidHeight']), SHELL_COURSE_HEIGHT= float(data['shellHieght']),
                                 TANK_DIAMETER= float(data['tankDiameter']), EnvironSensitivity= data['EnvSensitivity'], P_lvdike= float(data['fluidLeaveDike']),
                                 P_onsite= float(data['fluidOnsite']), P_offsite= float(data['fluidOffsite']), MATERIAL_COST= float(data['materialCostFactor']),
                                 API_COMPONENT_TYPE_NAME= data['apicomponenttypeid'], PRODUCTION_COST= float(data['productionCost']))
                rwcatank = RwCaTank(id= rwassessment, flow_rate_d1= cacal.W_n_Tank(1), flow_rate_d2= cacal.W_n_Tank(2), flow_rate_d3= cacal.W_n_Tank(3),
                                    flow_rate_d4= cacal.W_n_Tank(4), leak_duration_d1= cacal.ld_tank(1), leak_duration_d2= cacal.ld_tank(2),
                                    leak_duration_d3= cacal.ld_tank(3), leak_duration_d4= cacal.ld_tank(4),release_volume_leak_d1= cacal.Bbl_leak_n(1),
                                    release_volume_leak_d2= cacal.Bbl_leak_n(2), release_volume_leak_d3= cacal.Bbl_leak_n(3), release_volume_leak_d4= cacal.Bbl_leak_n(4),
                                    release_volume_rupture= cacal.Bbl_rupture_release(), liquid_height= cacal.FLUID_HEIGHT, volume_fluid= cacal.Bbl_total_shell(),
                                    time_leak_ground= cacal.ld_tank(4), volume_subsoil_leak_d1= cacal.Bbl_leak_release(), volume_subsoil_leak_d4= cacal.Bbl_rupture_release(),
                                    volume_ground_water_leak_d1= cacal.Bbl_leak_water(), volume_ground_water_leak_d4= cacal.Bbl_rupture_water(), barrel_dike_leak= cacal.Bbl_leak_indike(),
                                    barrel_dike_rupture= cacal.Bbl_rupture_indike(), barrel_onsite_leak= cacal.Bbl_leak_ssonsite(), barrel_onsite_rupture= cacal.Bbl_rupture_ssonsite(),
                                    barrel_offsite_leak= cacal.Bbl_leak_ssoffsite(), barrel_offsite_rupture= cacal.Bbl_rupture_ssoffsite(), barrel_water_leak= cacal.Bbl_leak_water(),
                                    barrel_water_rupture= cacal.Bbl_rupture_water(), fc_environ_leak= cacal.FC_leak_environ(), fc_environ_rupture= cacal.FC_rupture_environ(),
                                    fc_environ= cacal.FC_environ_shell(), material_factor= float(data['materialCostFactor']), component_damage_cost= cacal.fc_cmd(),
                                    business_cost= cacal.FC_PROD_SHELL(), consequence= cacal.FC_total_shell(), consequencecategory= cacal.FC_Category(cacal.FC_total_shell()))
                rwcatank.save()
                FC_TOTAL = cacal.FC_total_shell()
                FC_CATEGORY = cacal.FC_Category(cacal.FC_total_shell())
            else:
                cacal = CA_TANK_BOTTOM(Soil_type= data['soiltype'], TANK_FLUID= data['fluid'], Swg= float(data['distance']), TANK_DIAMETER= float(data['tankDiameter']),
                                       FLUID_HEIGHT= float(data['fluidHeight']), API_COMPONENT_TYPE_NAME=data['apicomponenttypeid'],
                                       PREVENTION_BARRIER= bool(preventBarrier), EnvironSensitivity= data['EnvSensitivity'], MATERIAL_COST= float(data['materialCostFactor']),
                                       PRODUCTION_COST= float(data['productionCost']), P_lvdike= float(data['fluidLeaveDike']), P_onsite= float(data['fluidOnsite']),
                                       P_offsite= float(data['fluidOffsite']))
                rwcatank = RwCaTank(id= rwassessment, hydraulic_water= cacal.k_h_water(), hydraulic_fluid= cacal.k_h_prod(),
                                    seepage_velocity= cacal.vel_s_prod(), flow_rate_d1= cacal.rate_n_tank_bottom(1), flow_rate_d4= cacal.rate_n_tank_bottom(4),
                                    leak_duration_d1= cacal.ld_n_tank_bottom(1), leak_duration_d4= cacal.ld_n_tank_bottom(4), release_volume_leak_d1= cacal.Bbl_leak_n_bottom(1),
                                    release_volume_leak_d4= cacal.Bbl_leak_n_bottom(4), release_volume_rupture= cacal.Bbl_rupture_release_bottom(),
                                    time_leak_ground= cacal.t_gl_bottom(), volume_subsoil_leak_d1= cacal.Bbl_leak_subsoil(1),
                                    volume_subsoil_leak_d4= cacal.Bbl_leak_subsoil(4), volume_ground_water_leak_d1= cacal.Bbl_leak_groundwater(1),
                                    volume_ground_water_leak_d4= cacal.Bbl_leak_groundwater(4), barrel_dike_rupture= cacal.Bbl_rupture_indike_bottom(),
                                    barrel_onsite_rupture= cacal.Bbl_rupture_ssonsite_bottom(), barrel_offsite_rupture= cacal.Bbl_rupture_ssoffsite_bottom(),
                                    barrel_water_rupture= cacal.Bbl_rupture_water_bottom(), fc_environ_leak= cacal.FC_leak_environ_bottom(),
                                    fc_environ_rupture= cacal.FC_rupture_environ_bottom(), fc_environ= cacal.FC_environ_bottom(), material_factor= float(data['materialCostFactor']),
                                    component_damage_cost= cacal.FC_cmd_bottom(), business_cost= cacal.FC_PROD_BOTTOM(), consequence= cacal.FC_total_bottom(),
                                    consequencecategory= cacal.FC_Category(cacal.FC_total_bottom()), liquid_height= cacal.FLUID_HEIGHT, volume_fluid= cacal.BBL_TOTAL_TANKBOTTOM())
                rwcatank.save()
                FC_TOTAL = cacal.FC_total_bottom()
                FC_CATEGORY = cacal.FC_Category(cacal.FC_total_bottom())

            TOTAL_DF_API1 = dm_cal.DF_TOTAL_API(0)
            TOTAL_DF_API2 = dm_cal.DF_TOTAL_API(3)
            TOTAL_DF_API3 = dm_cal.DF_TOTAL_API(6)
            gffTotal = api.gfftotal
            pofap1 = float(TOTAL_DF_API1) * float(dataFaci.managementfactor) * float(gffTotal)
            pofap2 = float(TOTAL_DF_API2) * float(dataFaci.managementfactor) * float(gffTotal)
            pofap3 = float(TOTAL_DF_API3) * float(dataFaci.managementfactor) * float(gffTotal)

            # thinningtype = General or Local
            refullPOF = RwFullPof(id=rwassessment, thinningap1=dm_cal.DF_THINNING_TOTAL_API(0),
                                  thinningap2=dm_cal.DF_THINNING_TOTAL_API(3),
                                  thinningap3=dm_cal.DF_THINNING_TOTAL_API(6),
                                  sccap1=dm_cal.DF_SSC_TOTAL_API(0), sccap2=dm_cal.DF_SSC_TOTAL_API(3),
                                  sccap3=dm_cal.DF_SSC_TOTAL_API(6),
                                  externalap1=dm_cal.DF_EXT_TOTAL_API(0), externalap2=dm_cal.DF_EXT_TOTAL_API(3),
                                  externalap3=dm_cal.DF_EXT_TOTAL_API(6),
                                  brittleap1=dm_cal.DF_BRIT_TOTAL_API(), brittleap2=dm_cal.DF_BRIT_TOTAL_API(),
                                  brittleap3=dm_cal.DF_BRIT_TOTAL_API(),
                                  htha_ap1=dm_cal.DF_HTHA_API(0), htha_ap2=dm_cal.DF_HTHA_API(3),
                                  htha_ap3=dm_cal.DF_HTHA_API(6),
                                  fatigueap1=dm_cal.DF_PIPE_API(), fatigueap2=dm_cal.DF_PIPE_API(),
                                  fatigueap3=dm_cal.DF_PIPE_API(),
                                  fms=dataFaci.managementfactor, thinningtype="Local",
                                  thinninglocalap1=max(dm_cal.DF_THINNING_TOTAL_API(0), dm_cal.DF_EXT_TOTAL_API(0)),
                                  thinninglocalap2=max(dm_cal.DF_THINNING_TOTAL_API(3), dm_cal.DF_EXT_TOTAL_API(3)),
                                  thinninglocalap3=max(dm_cal.DF_THINNING_TOTAL_API(6), dm_cal.DF_EXT_TOTAL_API(6)),
                                  thinninggeneralap1=dm_cal.DF_THINNING_TOTAL_API(0) + dm_cal.DF_EXT_TOTAL_API(0),
                                  thinninggeneralap2=dm_cal.DF_THINNING_TOTAL_API(3) + dm_cal.DF_EXT_TOTAL_API(3),
                                  thinninggeneralap3=dm_cal.DF_THINNING_TOTAL_API(6) + dm_cal.DF_EXT_TOTAL_API(6),
                                  totaldfap1=TOTAL_DF_API1, totaldfap2=TOTAL_DF_API2, totaldfap3=TOTAL_DF_API3,
                                  pofap1=pofap1, pofap2=pofap2, pofap3=pofap3, gfftotal=gffTotal,
                                  pofap1category=dm_cal.PoFCategory(TOTAL_DF_API1),
                                  pofap2category=dm_cal.PoFCategory(TOTAL_DF_API2),
                                  pofap3category=dm_cal.PoFCategory(TOTAL_DF_API3))
            refullPOF.save()

            # damage machinsm
            damageList = dm_cal.ISDF()
            for damage in damageList:
                damageMachinsm = RwDamageMechanism(id_dm= rwassessment, dmitemid_id=damage['DM_ITEM_ID'],
                                                   isactive=damage['isActive'],
                                                   df1=damage['DF1'], df2=damage['DF2'], df3=damage['DF3'],
                                                   highestinspectioneffectiveness=damage['highestEFF'],
                                                   secondinspectioneffectiveness=damage['secondEFF'],
                                                   numberofinspections=damage['numberINSP'],
                                                   lastinspdate=damage['lastINSP'].date().strftime('%Y-%m-%d'),
                                                   inspduedate=dm_cal.INSP_DUE_DATE(FC_TOTAL, gffTotal,
                                                                                    dataFaci.managementfactor,
                                                                                    dataFaciTarget.risktarget_fc).date().strftime('%Y-%m-%d'))
                damageMachinsm.save()

            refullfc = RwFullFcof(id=rwassessment, fcofvalue=FC_TOTAL, fcofcategory=FC_CATEGORY,
                                  prodcost=data['productionCost'])
            refullfc.save()

            if checkshell:
                return redirect('resultShell', rwassessment.id)
            else:
                return redirect('resultBottom', rwassessment.id)
    except ComponentMaster.DoesNotExist:
        raise Http404
    return render(request, 'home/new/newAllTank.html',{'component': dataCom, 'equipment':dataEq, 'commissiondate':commisiondate,'api':api,'data':data, 'facility':dataFaci, 'isShell':checkshell})

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
    return render(request, 'home/new/component.html', {'obj': dataEquip , 'componenttype': dataComponentType, 'api':dataApicomponent,'component':data, 'isedit':isEdit, 'error':error})

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
    elif "_export" in request.POST:
        for a in data:
            if(request.POST.get('%d' %a.siteid)):
                return redirect('exportFull', idx= a.siteid, status='Site')
        #return redirect('site_display')
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
        elif "_export" in request.POST:
            for a in data:
                if request.POST.get('%d' %a.facilityid):
                    return redirect('exportFull', idx= a.facilityid, status= 'Facility')
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
        elif "_export" in request.POST:
            for a in data:
                if request.POST.get('%d' %a.equipmentid):
                    return redirect('exportFull', idx=a.equipmentid, status='Equipment')
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
        elif "_export" in request.POST:
            for a in dataCom:
                if request.POST.get('%d' %a.componentid):
                    return redirect('exportFull', idx= a.componentid, status='Component')
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
    inputCa = RwInputCaLevel1.objects.get(id= proposalname)
    rwAss = RwAssessment.objects.get(id=proposalname)
    return render(request, 'display/FullyNormalConsequences.html', {'obj': ca,'inputCa': inputCa, 'assess':rwAss})

def displayShellConsequences(request, proposalname):
    shellConsequences = RwCaTank.objects.get(id = proposalname)
    rwAss = RwAssessment.objects.get(id = proposalname)
    return render(request, 'display/FullyShellConsequences.html', {'obj': shellConsequences, 'assess': rwAss})

def displayBottomConsequences(request, proposalname):
    bottomConsequences = RwCaTank.objects.get(id = proposalname)
    rwAss = RwAssessment.objects.get(id= proposalname)
    return render(request, 'display/TankBottomConsequences.html', {'obj': bottomConsequences, 'assess': rwAss})

def displayDF(request, proposalname):
    df = RwFullPof.objects.get(id= proposalname)
    return render(request, 'display/dfThinning.html', {'obj':df})

def displayFullDF(request, proposalname):
    df = RwFullPof.objects.get(id=proposalname)
    rwAss = RwAssessment.objects.get(id = proposalname)
    component = ComponentMaster.objects.get(componentid= rwAss.componentid_id)
    if component.componenttypeid_id == 8 or component.componenttypeid_id == 12  or component.componenttypeid_id == 14 or component.componenttypeid_id == 15:
        isTank = 1
    else:
        isTank = 0

    if component.componenttypeid_id == 8:
        isShell = 1
    else:
        isShell = 0

    return render(request, 'display/dfThinningFull.html', {'obj':df, 'assess': rwAss, 'isTank': isTank, 'isShell': isShell})

def displayProposal(request, componentname):
    proposal = RwAssessment.objects.filter(componentid= componentname)
    datafull = []
    component = ComponentMaster.objects.get(componentid= componentname)
    equipmen = EquipmentMaster.objects.get(equipmentid= component.equipmentid_id)
    for a in proposal:
        df = RwFullPof.objects.filter(id= a.id)
        fc = RwFullFcof.objects.filter(id = a.id)
        dm = RwDamageMechanism.objects.filter(id_dm= a.id)
        data = {}
        if df.count() != 0:
            data['DF'] = round(df[0].totaldfap1,2)
            data['gff'] = df[0].gfftotal
            data['fms'] = df[0].fms
        else:
            data['DF'] = 0
            data['gff'] = 0
            data['fms'] = 0
        if fc.count() != 0:
            data['FC'] = round(fc[0].fcofvalue,2)
        else:
            data['FC'] = 0

        if dm.count() != 0:
            #dataEq.commissiondate.date().strftime('%Y-%m-%d')
            data['DueDate'] = dm[0].inspduedate.date().strftime('%Y-%m-%d')
            data['LastInsp'] = dm[0].lastinspdate.date().strftime('%Y-%m-%d')
        else:
            data['DueDate'] = (a.assessmentdate.date() + relativedelta(years=15)).strftime('%Y-%m-%d')
            data['LastInsp'] = equipmen.commissiondate.date().strftime('%Y-%m-%d')

        data['risk'] = round(data['DF']*data['gff']*data['fms']*data['FC'],2)
        datafull.append(data)

    if component.componenttypeid_id == 8 or component.componenttypeid_id == 12  or component.componenttypeid_id == 14 or component.componenttypeid_id == 15:
        isTank = 1
    else:
        isTank = 0
    if component.componenttypeid_id == 8:
        isShell = 1
    else:
        isShell = 0
    zipped = zip(datafull,proposal)

    if "_delete" in request.POST:
        for a in proposal:
            if request.POST.get('%d' %a.id):
                a.delete()
        return redirect('proposalDisplay', componentname)
    elif "_export" in request.POST:
        for a in proposal:
            if request.POST.get('%d' %a.id):
                return redirect('export', a.id)
    return render(request, 'display/proposalDisplay.html', {'obj': zipped, 'componentid': componentname, 'component':component, 'isTank': isTank, 'isShell': isShell})

def displayRiskMap(request, proposalname):
    locatAPI1 = {}
    locatAPI2 = {}
    locatAPI3 = {}
    locatAPI1['x'] = 0
    locatAPI1['y'] = 500

    locatAPI2['x'] = 0
    locatAPI2['y'] = 500

    locatAPI3['x'] = 0
    locatAPI3['y'] = 500


    df = RwFullPof.objects.get(id= proposalname)
    ca = RwFullFcof.objects.get(id= proposalname)
    rwAss = RwAssessment.objects.get(id= proposalname)
    component = ComponentMaster.objects.get(componentid=rwAss.componentid_id)
    if component.componenttypeid_id == 8 or component.componenttypeid_id == 12 or component.componenttypeid_id == 14 or component.componenttypeid_id == 15:
        isTank = 1
    else:
        isTank = 0

    if component.componenttypeid_id == 8:
        isShell = 1
    else:
        isShell = 0
    Ca = round(ca.fcofvalue,2)
    DF1 = round(df.totaldfap1,2)
    DF2 = round(df.totaldfap2,2)
    DF3 = round(df.totaldfap3,2)
    return render(request, 'display/risk_Matrix.html', {'API1':location.locat(df.totaldfap1, ca.fcofvalue), 'API2':location.locat(df.totaldfap2, ca.fcofvalue), 'API3':location.locat(df.totaldfap3, ca.fcofvalue),'DF1': DF1,'DF2': DF2,'DF3': DF3, 'ca':Ca, 'ass':rwAss,'isTank': isTank, 'isShell': isShell, 'df':df})

######## Demo Export data

def exportDemo(request, proposalname):
    rwAss = RwAssessment.objects.get(id=proposalname)
    component = ComponentMaster.objects.get(componentid=rwAss.componentid_id)
    if component.componenttypeid_id == 8 or component.componenttypeid_id == 12 or component.componenttypeid_id == 14 or component.componenttypeid_id == 15:
        isTank = 1
    else:
        isTank = 0

    equip = EquipmentMaster.objects.get(equipmentid= component.equipmentid_id)

    fcof = RwFullFcof.objects.get(id=proposalname)
    fpof = RwFullPof.objects.get(id=proposalname)
    ca = export_data.convertCA(fcof.fcofvalue)
    df = export_data.convertDF(fpof.totaldfap1)
    dfFuture = export_data.convertDF(fpof.totaldfap2)
    risk = export_data.convertRisk(ca,df)
    riskFuture = export_data.convertRisk(ca,dfFuture)
    inspMethod= ['Inspection Type','ACFM',
                'Angled Compression Wave',
                'Angled Shear Wave',
                'A-scan Thickness Survey',
                'B-scan',
                'Chime',
                'Compton Scatter',
                'Crack Detection',
                'C-scan',
                'Digital Ultrasonic Thickness Gauge',
                'Endoscopy',
                'Gamma Radiography',
                'Hardness Surveys',
                'Hydrotesting',
                'Leak Detection',
                'Liquid Penetrant Inspection',
                'Lorus',
                'Low frequency',
                'Magnetic Fluorescent Inspection',
                'Magnetic Flux Leakage',
                'Magnetic Particle Inspection',
                'Microstructure Replication',
                'Naked Eye',
                'On-line Monitoring',
                'Passive Thermography',
                'Penetrant Leak Detection',
                'Pulsed',
                'Real-time Radiography',
                'Remote field',
                'Standard (flat coil)',
                'Surface Waves',
                'Teletest',
                'TOFD',
                'Transient Thermography',
                'Video',
                'X-Radiography']
    #if "xls" in request.POST:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Risk Summary')
    worksheet1 = workbook.add_worksheet('Risk Summary Detail')
    worksheet2 = workbook.add_worksheet('Inspection Plan')
    worksheet3 = workbook.add_worksheet('Lookup')

    format = workbook.add_format()
    format.set_font_name('Times New Roman')
    format.set_font_size(14)
    format.set_border()
    format.set_rotation(90)
    format.set_align('center')
    format.set_bg_color('#B7B7B7')

    format1 = workbook.add_format()
    format1.set_font_name('Times New Roman')
    format1.set_font_size(14)
    format1.set_border()
    format1.set_align('center')
    format1.set_align('vcenter')
    format1.set_bg_color('#B7B7B7')

    formatdata = workbook.add_format()
    formatdata.set_font_name('Times New Roman')
    formatdata.set_font_size(13)

    formattime = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    formatdata.set_font_name('Times New Roman')
    formattime.set_font_size(13)

    red = workbook.add_format({'bg_color':'#FF0000'})
    green = workbook.add_format({'bg_color':'#00FF00'})
    yellow = workbook.add_format({'bg_color':'#F9F400'})
    orange = workbook.add_format({'bg_color':'#FF9900'})
    gray = workbook.add_format({'bg_color':'#AAAAAA	'})

    ## Sheet lookup
    for i in range(1, len(inspMethod) + 1):
        worksheet3.write('A' + str(i), inspMethod[i - 1], formatdata)
    worksheet3.hide()

    ### SHEET CONTENT
    ### sheet 1 RiskSummary Ban Tho
    worksheet.merge_range('A1:D1', 'Indentification', format1)
    worksheet.set_column('A2:A2', 20)
    worksheet.set_column('C2:C2', 30)
    worksheet.set_column('B2:B2', 30)
    worksheet.set_column('D2:D2', 20)
    worksheet.write('A2', 'Equipment', format)
    worksheet.write('B2', 'Equipment Description', format)
    worksheet.write('C2', 'Equipment Type', format)
    worksheet.write('D2', 'Components', format)
    worksheet.merge_range('E1:E2', 'Represent.fluid', format)
    worksheet.merge_range('F1:F2', 'Fluid phase', format)
    worksheet.merge_range('G1:M1', 'Consequence (COF)', format1)
    worksheet.merge_range('O1:W1', 'Probability (POF)', format1)
    worksheet.merge_range('X1:Y1', 'Risk', format1)
    worksheet.write('G2', 'Current Risk', format)
    if isTank:
        worksheet.write('H2', 'Cofcat.Component Damage', format)
    else:
        worksheet.write('H2', 'Cofcat.Flammable', format)
    worksheet.write('I2', 'Cofcat.People', format)
    worksheet.write('J2', 'Cofcat.Asset', format)
    worksheet.write('K2', 'Cofcat.Env', format)
    worksheet.write('L2', 'Cofcat.Reputation', format)
    worksheet.write('M2', 'Cofcat.Combined', format)
    worksheet.merge_range('N1:N2', 'Component Material Glade', format)
    worksheet.write('O2', 'InitThinningPOFCatalog', format)
    worksheet.write('P2', 'InitEnv.Cracking', format)
    worksheet.write('Q2', 'InitOtherPOFCatalog', format)
    worksheet.write('R2', 'InitPOFCatelog', format)
    worksheet.write('S2', 'ExtThinningPOF', format)
    worksheet.write('T2', 'ExtEnvCrackingProbabilityCatelog', format)
    worksheet.write('U2', 'ExtOtherPOFCatelog', format)
    worksheet.write('V2', 'ExtPOFCatelog', format)
    worksheet.write('W2', 'POFCategory', format)
    worksheet.write('X2', 'Current Risk', format)
    worksheet.set_column('X2:X2', 20)
    worksheet.write('Y2', 'Future Risk', format)
    worksheet.set_column('Y2:Y2', 20)

    ### sheet 2 RiskSummary Ban Tinh
    worksheet1.merge_range('A1:D1', 'Indentification', format1)
    worksheet1.set_column('A2:A2', 20)
    worksheet1.set_column('C2:C2', 30)
    worksheet1.set_column('B2:B2', 30)
    worksheet1.set_column('D2:D2', 20)
    worksheet1.write('A2', 'Equipment', format)
    worksheet1.write('B2', 'Equipment Description', format)
    worksheet1.write('C2', 'Equipment Type', format)
    worksheet1.write('D2', 'Components', format)
    worksheet1.merge_range('E1:E2', 'Represent.fluid', format)
    worksheet1.merge_range('F1:F2', 'Fluid phase', format)
    worksheet1.merge_range('G1:M1', 'Consequence (COF), $', format1)
    worksheet1.merge_range('O1:W1', 'Probability (POF)', format1)
    worksheet1.merge_range('X1:Y1', 'Risk, $/year', format1)
    worksheet1.write('G2', 'Current Risk', format)
    worksheet1.write('H2', 'Cofcat.Flammable', format)
    worksheet1.write('I2', 'Cofcat.People', format)
    worksheet1.write('J2', 'Cofcat.Asset', format)
    worksheet1.write('K2', 'Cofcat.Env', format)
    worksheet1.write('L2', 'Cofcat.Reputation', format)
    worksheet1.write('M2', 'Cofcat.Combined', format)
    worksheet1.merge_range('N1:N2', 'Component Material Glade', format)
    worksheet1.write('O2', 'InitThinningPOFCatalog', format)
    worksheet1.write('P2', 'InitEnv.Cracking', format)
    worksheet1.write('Q2', 'InitOtherPOFCatalog', format)
    worksheet1.write('R2', 'InitPOFCatelog', format)
    worksheet1.write('S2', 'ExtThinningPOF', format)
    worksheet1.write('T2', 'ExtEnvCrackingProbabilityCatelog', format)
    worksheet1.write('U2', 'ExtOtherPOFCatelog', format)
    worksheet1.write('V2', 'ExtPOFCatelog', format)
    worksheet1.write('W2', 'POFCategory', format)
    worksheet1.write('X2', 'Current Risk', format)
    worksheet1.set_column('X2:X2', 20)
    worksheet1.write('Y2', 'Future Risk', format)
    worksheet1.set_column('Y2:Y2', 20)

    ### sheet 3 InspectionPlan
    worksheet2.set_row(0, 60)
    worksheet2.write('A1', 'System', format1)
    worksheet2.set_column('A1:A1', 20)
    worksheet2.write('B1', 'Equipment Name', format1)
    worksheet2.set_column('B1:B1', 20)
    worksheet2.write('C1', 'Damage Mechanism', format1)
    worksheet2.set_column('C1:C1', 30)
    worksheet2.write('D1', 'Method', format1)
    worksheet2.set_column('D1:D1', 20)
    worksheet2.write('E1', 'Coverage', format1)
    worksheet2.set_column('E1:E1', 50)
    worksheet2.write('F1', 'Availability', format1)
    worksheet2.set_column('F1:F1', 20)
    worksheet2.write('G1', 'Last Inspection Date', format1)
    worksheet2.set_column('G1:G1', 40)
    worksheet2.write('H1', 'Inspection Interval', format1)
    worksheet2.set_column('H1:H1', 30)
    worksheet2.write('I1', 'Due Date', format1)
    worksheet2.set_column('I1:I1', 20)

    ### VUNA EDIT
    data = RwFullPof.objects.filter(id=proposalname)
    if isTank:
        data1 = RwCaTank.objects.filter(id=proposalname)
        data2 = RwInputCaTank.objects.filter(id=proposalname)
    else:
        data1 = RwCaLevel1.objects.filter(id=proposalname)
        data2 = RwCaLevel1.objects.filter(id=proposalname)
    index = range(0, data.count())
    zipRisk = zip(data, data1, index, data2)

    worksheet.conditional_format('X3:Y' + str(data.count()),
                                 {'type': 'cell', 'criteria': '==', 'value': '"High"', 'format': red})
    worksheet.conditional_format('X3:Y' + str(data.count()),
                                 {'type': 'cell', 'criteria': '==', 'value': '"Medium High"', 'format': orange})
    worksheet.conditional_format('X3:Y' + str(data.count()),
                                 {'type': 'cell', 'criteria': '==', 'value': '"Medium"', 'format': yellow})
    worksheet.conditional_format('X3:Y' + str(data.count()),
                                 {'type': 'cell', 'criteria': '==', 'value': '"Low"', 'format': green})
    worksheet.conditional_format('X3:Y' + str(data.count()),
                                 {'type': 'cell', 'criteria': '==', 'value': '"N/A"', 'format': gray})
    for a, b, ind, c in zipRisk:
        i = 3 + ind
        # DF export
        worksheet.write('A' + str(i), equip.equipmentname, formatdata)
        worksheet.write('B' + str(i), equip.equipmentdesc, formatdata)
        worksheet.write('C' + str(i),
                        EquipmentType.objects.get(equipmenttypeid=equip.equipmenttypeid_id).equipmenttypename,
                        formatdata)
        worksheet.write('D' + str(i), component.componentname, formatdata)

        worksheet.write('O' + str(i), export_data.convertDF(a.thinningap1), formatdata)
        worksheet.write('P' + str(i), export_data.convertDF(a.sccap1), formatdata)
        worksheet.write('Q' + str(i), export_data.convertDF(a.htha_ap1 + a.brittleap1 + a.fatigueap1), formatdata)
        worksheet.write('R' + str(i), export_data.convertDF(a.thinningap1 + a.sccap1 + a.htha_ap1 + a.brittleap1), formatdata)
        worksheet.write('S' + str(i), export_data.convertDF(a.externalap1), formatdata)
        worksheet.write('T' + str(i), export_data.convertDF(0), formatdata)
        worksheet.write('U' + str(i), export_data.convertDF(0), formatdata)
        worksheet.write('V' + str(i), export_data.convertDF(a.externalap1), formatdata)
        worksheet.write('W' + str(i), export_data.convertDF(a.totaldfap1), formatdata)

        # Sheet1 demo
        worksheet1.write('A' + str(i), equip.equipmentnumber, formatdata)
        worksheet1.write('B' + str(i), equip.equipmentdesc, formatdata)
        worksheet1.write('C' + str(i),
                         EquipmentType.objects.get(equipmenttypeid=equip.equipmenttypeid_id).equipmenttypename,
                         formatdata)
        worksheet1.write('D' + str(i), component.componentname, formatdata)

        worksheet1.write('O' + str(i), a.thinningap1, formatdata)
        worksheet1.write('P' + str(i), a.sccap1, formatdata)
        worksheet1.write('Q' + str(i), a.htha_ap1 + a.brittleap1 + a.fatigueap1, formatdata)
        worksheet1.write('R' + str(i), a.thinningap1 + a.sccap1 + a.htha_ap1 + a.brittleap1, formatdata)
        worksheet1.write('S' + str(i), a.externalap1, formatdata)
        worksheet1.write('T' + str(i), 'N/A', formatdata)
        worksheet1.write('U' + str(i), 'N/A', formatdata)
        worksheet1.write('V' + str(i), a.externalap1, formatdata)
        worksheet1.write('W' + str(i), a.totaldfap1, formatdata)

        # CA export
        if isTank:
            worksheet.write('G' + str(i), "N/A", formatdata)
            worksheet.write('H' + str(i), export_data.convertCA(b.component_damage_cost), formatdata)
            worksheet.write('I' + str(i), 0, formatdata)
            worksheet.write('J' + str(i), export_data.convertCA(b.business_cost), formatdata)
            worksheet.write('K' + str(i), export_data.convertCA(b.fc_environ), formatdata)
            worksheet.write('L' + str(i), "N/A", formatdata)
            worksheet.write('M' + str(i), export_data.convertCA(b.consequence), formatdata)
            worksheet.write('E' + str(i), c.api_fluid, formatdata)
            worksheet.write('F' + str(i), 'Liquid', formatdata)
            # Sheet 1
            worksheet1.write('G' + str(i), "N/A", formatdata)
            worksheet1.write('H' + str(i), b.component_damage_cost, formatdata)
            worksheet1.write('I' + str(i), 0, formatdata)
            worksheet1.write('J' + str(i), b.business_cost, formatdata)
            worksheet1.write('K' + str(i), b.fc_environ, formatdata)
            worksheet1.write('L' + str(i), "N/A", formatdata)
            worksheet1.write('M' + str(i), b.consequence, formatdata)
            worksheet1.write('E' + str(i), c.api_fluid, formatdata)
            worksheet1.write('F' + str(i), 'Liquid', formatdata)
        else:
            worksheet.write('G' + str(i), "N/A", formatdata)
            worksheet.write('H' + str(i), export_data.convertCA(b.fc_cmd), formatdata)
            worksheet.write('I' + str(i), export_data.convertCA(b.fc_inj), formatdata)
            worksheet.write('J' + str(i), export_data.convertCA(b.fc_prod), formatdata)
            worksheet.write('K' + str(i), export_data.convertCA(b.fc_envi), formatdata)
            worksheet.write('L' + str(i), "N/A", formatdata)
            worksheet.write('M' + str(i), export_data.convertCA(b.fc_total), formatdata)
            worksheet.write('E' + str(i), c.api_fluid)
            worksheet.write('F' + str(i), c.system)
            # Sheet 1
            worksheet1.write('G' + str(i), "N/A", formatdata)
            worksheet1.write('H' + str(i), b.fc_cmd, formatdata)
            worksheet1.write('I' + str(i), b.fc_inj, formatdata)
            worksheet1.write('J' + str(i), b.fc_prod, formatdata)
            worksheet1.write('K' + str(i), b.fc_envi, formatdata)
            worksheet1.write('L' + str(i), "N/A", formatdata)
            worksheet1.write('M' + str(i), b.fc_total, formatdata)
            worksheet1.write('E' + str(i), c.api_fluid)
            worksheet1.write('F' + str(i), c.system)

        worksheet.write('X' + str(i), risk, formatdata)
        worksheet.write('Y' + str(i), riskFuture, formatdata)
        worksheet1.write('X' + str(i), fcof.fcofvalue * fpof.pofap1, formatdata)
        worksheet1.write('Y' + str(i), fcof.fcofvalue * fpof.pofap2, formatdata)

    inspInfo = RwDamageMechanism.objects.filter(id_dm=proposalname)
    lenght = range(0, inspInfo.count())
    inspZip = zip(inspInfo, lenght)
    if inspInfo.count() > 0:
        for a, b in inspZip:
            i = 2 + b
            worksheet2.write('A' + str(i), 'Inspection', formatdata)
            worksheet2.write('B' + str(i), equip.equipmentname, formatdata)
            worksheet2.write('C' + str(i), DmItems.objects.get(dmitemid=a.dmitemid_id).dmdescription, formatdata)
            worksheet2.write('D' + str(i), 'ACFM', formatdata)
            worksheet2.data_validation('D' + str(i), {'validate': 'list', 'source': '=Lookup!$A$2:$A$37'})
            worksheet2.write('E' + str(i), 'N/A', formatdata)
            worksheet2.write('F' + str(i), 'online', formatdata)
            worksheet2.data_validation('F' + str(i), {'validate': 'list',
                                                      'source': ['online', 'shutdown']})
            worksheet2.write('G' + str(i), a.lastinspdate.date(), formattime)
            worksheet2.write('H' + str(i), a.inspduedate.year - a.lastinspdate.year, formatdata)
            worksheet2.write('I' + str(i), a.inspduedate.date(), formattime)

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=myexport.xlsx'
    return response

def exportFull(request, idx, status):
    if status == 'Equipment':
        check = 1
    elif status == 'Faclity':
        check = 2
    elif status == 'Site':
        check = 3
    else:                   #Component Report
        check = 0
    name = 'N/A'
    inspMethod = ['Inspection Type', 'ACFM',
                  'Angled Compression Wave',
                  'Angled Shear Wave',
                  'A-scan Thickness Survey',
                  'B-scan',
                  'Chime',
                  'Compton Scatter',
                  'Crack Detection',
                  'C-scan',
                  'Digital Ultrasonic Thickness Gauge',
                  'Endoscopy',
                  'Gamma Radiography',
                  'Hardness Surveys',
                  'Hydrotesting',
                  'Leak Detection',
                  'Liquid Penetrant Inspection',
                  'Lorus',
                  'Low frequency',
                  'Magnetic Fluorescent Inspection',
                  'Magnetic Flux Leakage',
                  'Magnetic Particle Inspection',
                  'Microstructure Replication',
                  'Naked Eye',
                  'On-line Monitoring',
                  'Passive Thermography',
                  'Penetrant Leak Detection',
                  'Pulsed',
                  'Real-time Radiography',
                  'Remote field',
                  'Standard (flat coil)',
                  'Surface Waves',
                  'Teletest',
                  'TOFD',
                  'Transient Thermography',
                  'Video',
                  'X-Radiography']
    # if "xls" in request.POST:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Risk Summary')
    worksheet1 = workbook.add_worksheet('Risk Summary Detail')
    worksheet2 = workbook.add_worksheet('Inspection Plan')
    worksheet3 = workbook.add_worksheet('Lookup')

    format = workbook.add_format()
    format.set_font_name('Times New Roman')
    format.set_font_size(14)
    format.set_border()
    format.set_rotation(90)
    format.set_align('center')
    format.set_bg_color('#B7B7B7')

    format1 = workbook.add_format()
    format1.set_font_name('Times New Roman')
    format1.set_font_size(14)
    format1.set_border()
    format1.set_align('center')
    format1.set_align('vcenter')
    format1.set_bg_color('#B7B7B7')

    formatdata = workbook.add_format()
    formatdata.set_font_name('Times New Roman')
    formatdata.set_font_size(13)

    formattime = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    formatdata.set_font_name('Times New Roman')
    formattime.set_font_size(13)

    red = workbook.add_format({'bg_color': '#FF0000'})
    green = workbook.add_format({'bg_color': '#00FF00'})
    yellow = workbook.add_format({'bg_color': '#F9F400'})
    orange = workbook.add_format({'bg_color': '#FF9900'})
    gray = workbook.add_format({'bg_color': '#AAAAAA'})

    ## Sheet lookup
    for i in range(1, len(inspMethod) + 1):
        worksheet3.write('A' + str(i), inspMethod[i - 1], formatdata)
    worksheet3.hide()

    ### SHEET CONTENT
    ### sheet 1 RiskSummary Ban Tho
    worksheet.merge_range('A1:D1', 'Indentification', format1)
    worksheet.set_column('A2:A2', 20)
    worksheet.set_column('C2:C2', 30)
    worksheet.set_column('B2:B2', 30)
    worksheet.set_column('D2:D2', 20)
    worksheet.write('A2', 'Equipment', format)
    worksheet.write('B2', 'Equipment Description', format)
    worksheet.write('C2', 'Equipment Type', format)
    worksheet.write('D2', 'Components', format)
    worksheet.merge_range('E1:E2', 'Represent.fluid', format)
    worksheet.merge_range('F1:F2', 'Fluid phase', format)
    worksheet.merge_range('G1:M1', 'Consequence (COF)', format1)
    worksheet.merge_range('O1:W1', 'Probability (POF)', format1)
    worksheet.merge_range('X1:Y1', 'Risk', format1)
    worksheet.write('G2', 'Current Risk', format)
    worksheet.write('H2', 'Cofcat.Flammable', format)
    worksheet.write('I2', 'Cofcat.People', format)
    worksheet.write('J2', 'Cofcat.Asset', format)
    worksheet.write('K2', 'Cofcat.Env', format)
    worksheet.write('L2', 'Cofcat.Reputation', format)
    worksheet.write('M2', 'Cofcat.Combined', format)
    worksheet.merge_range('N1:N2', 'Component Material Glade', format)
    worksheet.write('O2', 'InitThinningPOFCatalog', format)
    worksheet.write('P2', 'InitEnv.Cracking', format)
    worksheet.write('Q2', 'InitOtherPOFCatalog', format)
    worksheet.write('R2', 'InitPOFCatelog', format)
    worksheet.write('S2', 'ExtThinningPOF', format)
    worksheet.write('T2', 'ExtEnvCrackingProbabilityCatelog', format)
    worksheet.write('U2', 'ExtOtherPOFCatelog', format)
    worksheet.write('V2', 'ExtPOFCatelog', format)
    worksheet.write('W2', 'POFCategory', format)
    worksheet.write('X2', 'Current Risk', format)
    worksheet.set_column('X2:X2', 20)
    worksheet.write('Y2', 'Future Risk', format)
    worksheet.set_column('Y2:Y2', 20)

    ### sheet 2 RiskSummary Ban Tinh
    worksheet1.merge_range('A1:D1', 'Indentification', format1)
    worksheet1.set_column('A2:A2', 20)
    worksheet1.set_column('C2:C2', 30)
    worksheet1.set_column('B2:B2', 30)
    worksheet1.set_column('D2:D2', 20)
    worksheet1.write('A2', 'Equipment', format)
    worksheet1.write('B2', 'Equipment Description', format)
    worksheet1.write('C2', 'Equipment Type', format)
    worksheet1.write('D2', 'Components', format)
    worksheet1.merge_range('E1:E2', 'Represent.fluid', format)
    worksheet1.merge_range('F1:F2', 'Fluid phase', format)
    worksheet1.merge_range('G1:M1', 'Consequence (COF), $', format1)
    worksheet1.merge_range('O1:W1', 'Probability (POF)', format1)
    worksheet1.merge_range('X1:Y1', 'Risk, $/year', format1)
    worksheet1.write('G2', 'Current Risk', format)
    worksheet1.write('H2', 'Cofcat.Flammable', format)
    worksheet1.write('I2', 'Cofcat.People', format)
    worksheet1.write('J2', 'Cofcat.Asset', format)
    worksheet1.write('K2', 'Cofcat.Env', format)
    worksheet1.write('L2', 'Cofcat.Reputation', format)
    worksheet1.write('M2', 'Cofcat.Combined', format)
    worksheet1.merge_range('N1:N2', 'Component Material Glade', format)
    worksheet1.write('O2', 'InitThinningPOFCatalog', format)
    worksheet1.write('P2', 'InitEnv.Cracking', format)
    worksheet1.write('Q2', 'InitOtherPOFCatalog', format)
    worksheet1.write('R2', 'InitPOFCatelog', format)
    worksheet1.write('S2', 'ExtThinningPOF', format)
    worksheet1.write('T2', 'ExtEnvCrackingProbabilityCatelog', format)
    worksheet1.write('U2', 'ExtOtherPOFCatelog', format)
    worksheet1.write('V2', 'ExtPOFCatelog', format)
    worksheet1.write('W2', 'POFCategory', format)
    worksheet1.write('X2', 'Current Risk', format)
    worksheet1.set_column('X2:X2', 20)
    worksheet1.write('Y2', 'Future Risk', format)
    worksheet1.set_column('Y2:Y2', 20)

    ### sheet 3 InspectionPlan
    worksheet2.set_row(0, 60)
    worksheet2.write('A1', 'System', format1)
    worksheet2.set_column('A1:A1', 20)
    worksheet2.write('B1', 'Equipment Name', format1)
    worksheet2.set_column('B1:B1', 20)
    worksheet2.write('C1', 'Damage Mechanism', format1)
    worksheet2.set_column('C1:C1', 30)
    worksheet2.write('D1', 'Method', format1)
    worksheet2.set_column('D1:D1', 20)
    worksheet2.write('E1', 'Coverage', format1)
    worksheet2.set_column('E1:E1', 50)
    worksheet2.write('F1', 'Availability', format1)
    worksheet2.set_column('F1:F1', 20)
    worksheet2.write('G1', 'Last Inspection Date', format1)
    worksheet2.set_column('G1:G1', 40)
    worksheet2.write('H1', 'Inspection Interval, years', format1)
    worksheet2.set_column('H1:H1', 30)
    worksheet2.write('I1', 'Due Date', format1)
    worksheet2.set_column('I1:I1', 20)


    ############### PROCCESSING DATA#################
    # if Component
    if check == 0:
        dataC = export_data.getC_risk(idx)
        insp_C = export_data.getC_insp(idx)
        insp_ind = 2
        name = ComponentMaster.objects.get(componentid= idx).componentname
        if dataC is not None:
            worksheet.write('A3', dataC['equipment_name'], formatdata)
            worksheet.write('B3', dataC['equipment_desc'], formatdata)
            worksheet.write('C3', dataC['equipment_type'], formatdata)
            worksheet.write('D3', dataC['component_name'], formatdata)
            worksheet.write('O3', export_data.convertDF(dataC['init_thinning']), formatdata)
            worksheet.write('P3', export_data.convertDF(dataC['init_cracking']), formatdata)
            worksheet.write('Q3', export_data.convertDF(dataC['init_other']), formatdata)
            worksheet.write('R3', export_data.convertDF(dataC['init_pof']), formatdata)
            worksheet.write('S3', export_data.convertDF(dataC['ext_thinning']), formatdata)
            worksheet.write('T3', export_data.convertDF(0), formatdata)
            worksheet.write('U3', export_data.convertDF(0), formatdata)
            worksheet.write('V3', export_data.convertDF(dataC['pof_catalog']), formatdata)
            worksheet.write('E3', dataC['fluid'], formatdata)
            worksheet.write('F3', dataC['fluid_phase'], formatdata)
            worksheet.write('G3', 'N/A', formatdata)
            worksheet.write('H3', export_data.convertCA(dataC['flamable']), formatdata)
            worksheet.write('I3', export_data.convertCA(dataC['inj']), formatdata)
            worksheet.write('J3', export_data.convertCA(dataC['business']), formatdata)
            worksheet.write('K3', export_data.convertCA(dataC['env']), formatdata)
            worksheet.write('L3', 'N/A', formatdata)
            worksheet.write('M3', export_data.convertCA(dataC['consequence']), formatdata)
            worksheet.write('X3', export_data.convertRisk(export_data.convertCA(dataC['consequence']), export_data.convertDF(dataC['pof_catalog'])), formatdata)
            worksheet.write('Y3', export_data.convertRisk(export_data.convertCA(dataC['consequence']), export_data.convertDF(dataC['pof_catalog2'])), formatdata)

            worksheet1.write('A3', dataC['equipment_name'], formatdata)
            worksheet1.write('B3', dataC['equipment_desc'], formatdata)
            worksheet1.write('C3', dataC['equipment_type'], formatdata)
            worksheet1.write('D3', dataC['component_name'], formatdata)
            worksheet1.write('O3', dataC['init_thinning'], formatdata)
            worksheet1.write('P3', dataC['init_cracking'], formatdata)
            worksheet1.write('Q3', dataC['init_other'], formatdata)
            worksheet1.write('R3', dataC['init_pof'], formatdata)
            worksheet1.write('S3', dataC['ext_thinning'], formatdata)
            worksheet1.write('T3', 'N/A', formatdata)
            worksheet1.write('U3', 'N/A', formatdata)
            worksheet1.write('V3', dataC['pof_catalog'], formatdata)
            worksheet1.write('E3', dataC['fluid'], formatdata)
            worksheet1.write('F3', dataC['fluid_phase'], formatdata)
            worksheet1.write('G3', 'N/A', formatdata)
            worksheet1.write('H3', dataC['flamable'], formatdata)
            worksheet1.write('I3', dataC['inj'], formatdata)
            worksheet1.write('J3', dataC['business'], formatdata)
            worksheet1.write('K3', dataC['env'], formatdata)
            worksheet1.write('L3', 'N/A', formatdata)
            worksheet1.write('M3', dataC['consequence'], formatdata)
            worksheet1.write('X3', dataC['risk'], formatdata)
            worksheet1.write('Y3', dataC['risk_future'], formatdata)

        worksheet.conditional_format('X3:Y3',
                                     {'type': 'cell', 'criteria': '==', 'value': '"High"', 'format': red})
        worksheet.conditional_format('X3:Y3',
                                     {'type': 'cell', 'criteria': '==', 'value': '"Medium High"', 'format': orange})
        worksheet.conditional_format('X3:Y3',
                                     {'type': 'cell', 'criteria': '==', 'value': '"Medium"', 'format': yellow})
        worksheet.conditional_format('X3:Y3',
                                     {'type': 'cell', 'criteria': '==', 'value': '"Low"', 'format': green})
        worksheet.conditional_format('X3:Y3',
                                     {'type': 'cell', 'criteria': '==', 'value': '"N/A"', 'format': gray})

        if insp_C is not None:
            for insp in insp_C:
                if insp is not None:
                    worksheet2.write('A' + str(insp_ind) , insp['System'], formatdata)
                    worksheet2.write('B' + str(insp_ind), insp['Equipment'], formatdata)
                    worksheet2.write('C' + str(insp_ind), insp['Damage'],
                                     formatdata)
                    worksheet2.write('D' + str(insp_ind), insp['Method'], formatdata)
                    worksheet2.data_validation('D' + str(insp_ind), {'validate': 'list', 'source': '=Lookup!$A$2:$A$37'})
                    worksheet2.write('E' + str(insp_ind), insp['Coverage'], formatdata)
                    worksheet2.write('F' + str(insp_ind), insp['Avaiable'], formatdata)
                    worksheet2.data_validation('F' + str(insp_ind), {'validate': 'list',
                                                              'source': ['online', 'shutdown']})
                    worksheet2.write('G' + str(insp_ind), insp['Last'], formattime)
                    worksheet2.write('H' + str(insp_ind), insp['Interval'], formatdata)
                    worksheet2.write('I' + str(insp_ind), insp['Duedate'], formattime)
                    insp_ind += 1
    # if Equipment
    elif check == 1:
        dataE = export_data.getE_risk(idx)
        insp_E = export_data.getE_insp(idx)
        name = EquipmentMaster.objects.get(equipmentid= idx).equipmentname
        ind = 3
        insp_ind = 2
        if dataE is not None:
            for dataC in dataE:
                if dataC is not None:
                    worksheet.write('A' + str(ind), (dataC['equipment_name']), formatdata)
                    worksheet.write('B' + str(ind), (dataC['equipment_desc']), formatdata)
                    worksheet.write('C' + str(ind), (dataC['equipment_type']), formatdata)
                    worksheet.write('D' + str(ind), (dataC['component_name']), formatdata)
                    worksheet.write('O' + str(ind), export_data.convertDF(dataC['init_thinning']), formatdata)
                    worksheet.write('P' + str(ind), export_data.convertDF(dataC['init_cracking']), formatdata)
                    worksheet.write('Q' + str(ind), export_data.convertDF(dataC['init_other']), formatdata)
                    worksheet.write('R' + str(ind), export_data.convertDF(dataC['init_pof']), formatdata)
                    worksheet.write('S' + str(ind), export_data.convertDF(dataC['ext_thinning']), formatdata)
                    worksheet.write('T' + str(ind), export_data.convertDF(0), formatdata)
                    worksheet.write('U' + str(ind), export_data.convertDF(0), formatdata)
                    worksheet.write('V' + str(ind), export_data.convertDF(dataC['pof_catalog']), formatdata)
                    worksheet.write('E' + str(ind), dataC['fluid'], formatdata)
                    worksheet.write('F' + str(ind), dataC['fluid_phase'], formatdata)
                    worksheet.write('G' + str(ind), 'N/A', formatdata)
                    worksheet.write('H' + str(ind), export_data.convertCA(dataC['flamable']), formatdata)
                    worksheet.write('I' + str(ind), export_data.convertCA(dataC['inj']), formatdata)
                    worksheet.write('J' + str(ind), export_data.convertCA(dataC['business']), formatdata)
                    worksheet.write('K' + str(ind), export_data.convertCA(dataC['env']), formatdata)
                    worksheet.write('L' + str(ind), 'N/A', formatdata)
                    worksheet.write('M' + str(ind), export_data.convertCA(dataC['consequence']), formatdata)
                    worksheet.write('X' + str(ind), export_data.convertRisk(export_data.convertCA(dataC['consequence']), export_data.convertDF(dataC['pof_catalog'])), formatdata)
                    worksheet.write('Y' + str(ind), export_data.convertRisk(export_data.convertCA(dataC['consequence']), export_data.convertDF(dataC['pof_catalog2'])), formatdata)

                    worksheet1.write('A' + str(ind), dataC['equipment_name'], formatdata)
                    worksheet1.write('B' + str(ind), dataC['equipment_desc'], formatdata)
                    worksheet1.write('C' + str(ind), dataC['equipment_type'], formatdata)
                    worksheet1.write('D' + str(ind), dataC['component_name'], formatdata)
                    worksheet1.write('O' + str(ind), dataC['init_thinning'], formatdata)
                    worksheet1.write('P' + str(ind), dataC['init_cracking'], formatdata)
                    worksheet1.write('Q' + str(ind), dataC['init_other'], formatdata)
                    worksheet1.write('R' + str(ind), dataC['init_pof'], formatdata)
                    worksheet1.write('S' + str(ind), dataC['ext_thinning'], formatdata)
                    worksheet1.write('T' + str(ind), 'N/A', formatdata)
                    worksheet1.write('U' + str(ind), 'N/A', formatdata)
                    worksheet1.write('V' + str(ind), dataC['pof_catalog'], formatdata)
                    worksheet1.write('E' + str(ind), dataC['fluid'], formatdata)
                    worksheet1.write('F' + str(ind), dataC['fluid_phase'], formatdata)
                    worksheet1.write('G' + str(ind), 'N/A', formatdata)
                    worksheet1.write('H' + str(ind), dataC['flamable'], formatdata)
                    worksheet1.write('I' + str(ind), dataC['inj'], formatdata)
                    worksheet1.write('J' + str(ind), dataC['business'], formatdata)
                    worksheet1.write('K' + str(ind), dataC['env'], formatdata)
                    worksheet1.write('L' + str(ind), 'N/A', formatdata)
                    worksheet1.write('M' + str(ind), dataC['consequence'], formatdata)
                    worksheet1.write('X' + str(ind), dataC['risk'], formatdata)
                    worksheet1.write('Y' + str(ind), dataC['risk_future'], formatdata)
                    ind += 1
                worksheet.conditional_format('X3:Y' + str(ind),
                                             {'type': 'cell', 'criteria': '==', 'value': '"High"', 'format': red})
                worksheet.conditional_format('X3:Y' + str(ind),
                                             {'type': 'cell', 'criteria': '==', 'value': '"Medium High"',
                                              'format': orange})
                worksheet.conditional_format('X3:Y' + str(ind),
                                             {'type': 'cell', 'criteria': '==', 'value': '"Medium"', 'format': yellow})
                worksheet.conditional_format('X3:Y' + str(ind),
                                             {'type': 'cell', 'criteria': '==', 'value': '"Low"', 'format': green})
                worksheet.conditional_format('X3:Y' + str(ind),
                                             {'type': 'cell', 'criteria': '==', 'value': '"N/A"', 'format': gray})
        if insp_E is not None:
            for C in insp_E:
                if C is not None:
                    for insp in C:
                        if insp is not None:
                            worksheet2.write('A' + str(insp_ind), insp['System'], formatdata)
                            worksheet2.write('B' + str(insp_ind), insp['Equipment'], formatdata)
                            worksheet2.write('C' + str(insp_ind), insp['Damage'],
                                             formatdata)
                            worksheet2.write('D' + str(insp_ind), insp['Method'], formatdata)
                            worksheet2.data_validation('D' + str(insp_ind),
                                                       {'validate': 'list', 'source': '=Lookup!$A$2:$A$37'})
                            worksheet2.write('E' + str(insp_ind), insp['Coverage'], formatdata)
                            worksheet2.write('F' + str(insp_ind), insp['Avaiable'], formatdata)
                            worksheet2.data_validation('F' + str(insp_ind), {'validate': 'list',
                                                                             'source': ['online', 'shutdown']})
                            worksheet2.write('G' + str(insp_ind), insp['Last'], formattime)
                            worksheet2.write('H' + str(insp_ind), insp['Interval'], formatdata)
                            worksheet2.write('I' + str(insp_ind), insp['Duedate'], formattime)
                            insp_ind += 1
    # if Facility
    elif check == 2:
        dataF = export_data.getF_risk(idx)
        insp_F = export_data.getF_insp(idx)
        name = Facility.objects.get(facilityid= idx).facilityname
        ind = 3
        insp_ind = 2
        if dataF is not None:
            for dataE in dataF:
                if dataE is not None:
                    for dataC in dataE:
                        if dataC is not None:
                            worksheet.write('A' + str(ind), (dataC['equipment_name']), formatdata)
                            worksheet.write('B' + str(ind), (dataC['equipment_desc']), formatdata)
                            worksheet.write('C' + str(ind), (dataC['equipment_type']), formatdata)
                            worksheet.write('D' + str(ind), (dataC['component_name']), formatdata)
                            worksheet.write('O' + str(ind), export_data.convertDF(dataC['init_thinning']), formatdata)
                            worksheet.write('P' + str(ind), export_data.convertDF(dataC['init_cracking']), formatdata)
                            worksheet.write('Q' + str(ind), export_data.convertDF(dataC['init_other']), formatdata)
                            worksheet.write('R' + str(ind), export_data.convertDF(dataC['init_pof']), formatdata)
                            worksheet.write('S' + str(ind), export_data.convertDF(dataC['ext_thinning']), formatdata)
                            worksheet.write('T' + str(ind), export_data.convertDF(0), formatdata)
                            worksheet.write('U' + str(ind), export_data.convertDF(0), formatdata)
                            worksheet.write('V' + str(ind), export_data.convertDF(dataC['pof_catalog']), formatdata)
                            worksheet.write('E' + str(ind), dataC['fluid'], formatdata)
                            worksheet.write('F' + str(ind), dataC['fluid_phase'], formatdata)
                            worksheet.write('G' + str(ind), 'N/A', formatdata)
                            worksheet.write('H' + str(ind), export_data.convertCA(dataC['flamable']), formatdata)
                            worksheet.write('I' + str(ind), export_data.convertCA(dataC['inj']), formatdata)
                            worksheet.write('J' + str(ind), export_data.convertCA(dataC['business']), formatdata)
                            worksheet.write('K' + str(ind), export_data.convertCA(dataC['env']), formatdata)
                            worksheet.write('L' + str(ind), 'N/A', formatdata)
                            worksheet.write('M' + str(ind), export_data.convertCA(dataC['consequence']), formatdata)
                            worksheet.write('X' + str(ind), export_data.convertRisk(export_data.convertCA(dataC['consequence']), export_data.convertDF(dataC['pof_catalog'])),
                                            formatdata)
                            worksheet.write('Y' + str(ind), export_data.convertRisk(export_data.convertCA(dataC['consequence']), export_data.convertDF(dataC['pof_catalog2'])),
                                            formatdata)

                            worksheet1.write('A' + str(ind), dataC['equipment_name'], formatdata)
                            worksheet1.write('B' + str(ind), dataC['equipment_desc'], formatdata)
                            worksheet1.write('C' + str(ind), dataC['equipment_type'], formatdata)
                            worksheet1.write('D' + str(ind), dataC['component_name'], formatdata)
                            worksheet1.write('O' + str(ind), dataC['init_thinning'], formatdata)
                            worksheet1.write('P' + str(ind), dataC['init_cracking'], formatdata)
                            worksheet1.write('Q' + str(ind), dataC['init_other'], formatdata)
                            worksheet1.write('R' + str(ind), dataC['init_pof'], formatdata)
                            worksheet1.write('S' + str(ind), dataC['ext_thinning'], formatdata)
                            worksheet1.write('T' + str(ind), 'N/A', formatdata)
                            worksheet1.write('U' + str(ind), 'N/A', formatdata)
                            worksheet1.write('V' + str(ind), dataC['pof_catalog'], formatdata)
                            worksheet1.write('E' + str(ind), dataC['fluid'], formatdata)
                            worksheet1.write('F' + str(ind), dataC['fluid_phase'], formatdata)
                            worksheet1.write('G' + str(ind), 'N/A', formatdata)
                            worksheet1.write('H' + str(ind), dataC['flamable'], formatdata)
                            worksheet1.write('I' + str(ind), dataC['inj'], formatdata)
                            worksheet1.write('J' + str(ind), dataC['business'], formatdata)
                            worksheet1.write('K' + str(ind), dataC['env'], formatdata)
                            worksheet1.write('L' + str(ind), 'N/A', formatdata)
                            worksheet1.write('M' + str(ind), dataC['consequence'], formatdata)
                            worksheet1.write('X' + str(ind), dataC['risk'], formatdata)
                            worksheet1.write('Y' + str(ind), dataC['risk_future'], formatdata)
                            ind += 1
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"High"', 'format': red})
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"Medium High"',
                                          'format': orange})
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"Medium"', 'format': yellow})
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"Low"', 'format': green})
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"N/A"', 'format': gray})
        if insp_F is not None:
            for E in insp_F:
                if E is not None:
                    for C in E:
                        if C is not None:
                            for insp in C:
                                if insp is not None:
                                    worksheet2.write('A' + str(insp_ind), insp['System'], formatdata)
                                    worksheet2.write('B' + str(insp_ind), insp['Equipment'], formatdata)
                                    worksheet2.write('C' + str(insp_ind), insp['Damage'],
                                                     formatdata)
                                    worksheet2.write('D' + str(insp_ind), insp['Method'], formatdata)
                                    worksheet2.data_validation('D' + str(insp_ind),
                                                               {'validate': 'list', 'source': '=Lookup!$A$2:$A$37'})
                                    worksheet2.write('E' + str(insp_ind), insp['Coverage'], formatdata)
                                    worksheet2.write('F' + str(insp_ind), insp['Avaiable'], formatdata)
                                    worksheet2.data_validation('F' + str(insp_ind), {'validate': 'list',
                                                                                     'source': ['online', 'shutdown']})
                                    worksheet2.write('G' + str(insp_ind), insp['Last'], formattime)
                                    worksheet2.write('H' + str(insp_ind), insp['Interval'], formatdata)
                                    worksheet2.write('I' + str(insp_ind), insp['Duedate'], formattime)
                                    insp_ind += 1

    else:
        dataS = export_data.getS_risk(idx)
        insp_S = export_data.getS_insp(idx)
        name = Sites.objects.get(siteid= idx).sitename
        ind = 3
        insp_ind = 2
        if dataS is not None:
            for dataF in dataS:
                if dataF is not None:
                    for dataE in dataF:
                        if dataE is not None:
                            for dataC in dataE:
                                if dataC is not None:
                                    worksheet.write('A' + str(ind), (dataC['equipment_name']), formatdata)
                                    worksheet.write('B' + str(ind), (dataC['equipment_desc']), formatdata)
                                    worksheet.write('C' + str(ind), (dataC['equipment_type']), formatdata)
                                    worksheet.write('D' + str(ind), (dataC['component_name']), formatdata)
                                    worksheet.write('O' + str(ind), export_data.convertDF(dataC['init_thinning']), formatdata)
                                    worksheet.write('P' + str(ind), export_data.convertDF(dataC['init_cracking']), formatdata)
                                    worksheet.write('Q' + str(ind), export_data.convertDF(dataC['init_other']), formatdata)
                                    worksheet.write('R' + str(ind), export_data.convertDF(dataC['init_pof']), formatdata)
                                    worksheet.write('S' + str(ind), export_data.convertDF(dataC['ext_thinning']), formatdata)
                                    worksheet.write('T' + str(ind), export_data.convertDF(0), formatdata)
                                    worksheet.write('U' + str(ind), export_data.convertDF(0), formatdata)
                                    worksheet.write('V' + str(ind), export_data.convertDF(dataC['pof_catalog']), formatdata)
                                    worksheet.write('E' + str(ind), dataC['fluid'], formatdata)
                                    worksheet.write('F' + str(ind), dataC['fluid_phase'], formatdata)
                                    worksheet.write('G' + str(ind), 'N/A', formatdata)
                                    worksheet.write('H' + str(ind), export_data.convertCA(dataC['flamable']), formatdata)
                                    worksheet.write('I' + str(ind), export_data.convertCA(dataC['inj']), formatdata)
                                    worksheet.write('J' + str(ind), export_data.convertCA(dataC['business']), formatdata)
                                    worksheet.write('K' + str(ind), export_data.convertCA(dataC['env']), formatdata)
                                    worksheet.write('L' + str(ind), 'N/A', formatdata)
                                    worksheet.write('M' + str(ind), export_data.convertCA(dataC['consequence']), formatdata)
                                    worksheet.write('X' + str(ind), export_data.convertRisk(export_data.convertCA(dataC['consequence']), export_data.convertDF(dataC['pof_catalog'])),
                                                    formatdata)
                                    worksheet.write('Y' + str(ind),
                                                    export_data.convertRisk(export_data.convertCA(dataC['consequence']),
                                                                            export_data.convertDF(dataC['pof_catalog2'])),
                                                    formatdata)

                                    worksheet1.write('A' + str(ind), dataC['equipment_name'], formatdata)
                                    worksheet1.write('B' + str(ind), dataC['equipment_desc'], formatdata)
                                    worksheet1.write('C' + str(ind), dataC['equipment_type'], formatdata)
                                    worksheet1.write('D' + str(ind), dataC['component_name'], formatdata)
                                    worksheet1.write('O' + str(ind), dataC['init_thinning'], formatdata)
                                    worksheet1.write('P' + str(ind), dataC['init_cracking'], formatdata)
                                    worksheet1.write('Q' + str(ind), dataC['init_other'], formatdata)
                                    worksheet1.write('R' + str(ind), dataC['init_pof'], formatdata)
                                    worksheet1.write('S' + str(ind), dataC['ext_thinning'], formatdata)
                                    worksheet1.write('T' + str(ind), 'N/A', formatdata)
                                    worksheet1.write('U' + str(ind), 'N/A', formatdata)
                                    worksheet1.write('V' + str(ind), dataC['pof_catalog'], formatdata)
                                    worksheet1.write('E' + str(ind), dataC['fluid'], formatdata)
                                    worksheet1.write('F' + str(ind), dataC['fluid_phase'], formatdata)
                                    worksheet1.write('G' + str(ind), 'N/A', formatdata)
                                    worksheet1.write('H' + str(ind), dataC['flamable'], formatdata)
                                    worksheet1.write('I' + str(ind), dataC['inj'], formatdata)
                                    worksheet1.write('J' + str(ind), dataC['business'], formatdata)
                                    worksheet1.write('K' + str(ind), dataC['env'], formatdata)
                                    worksheet1.write('L' + str(ind), 'N/A', formatdata)
                                    worksheet1.write('M' + str(ind), dataC['consequence'], formatdata)
                                    worksheet1.write('X' + str(ind), dataC['risk'], formatdata)
                                    worksheet1.write('Y' + str(ind), dataC['risk_future'], formatdata)
                                    ind += 1
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"High"', 'format': red})
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"Medium High"',
                                          'format': orange})
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"Medium"', 'format': yellow})
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"Low"', 'format': green})
            worksheet.conditional_format('X3:Y' + str(ind),
                                         {'type': 'cell', 'criteria': '==', 'value': '"N/A"', 'format': gray})
        if insp_S is not None:
            for F in insp_S:
                if F is not None:
                    for E in F:
                        if E is not None:
                            for C in E:
                                if C is not None:
                                    for insp in C:
                                        if insp is not None:
                                            worksheet2.write('A' + str(insp_ind), insp['System'], formatdata)
                                            worksheet2.write('B' + str(insp_ind), insp['Equipment'], formatdata)
                                            worksheet2.write('C' + str(insp_ind), insp['Damage'],
                                                             formatdata)
                                            worksheet2.write('D' + str(insp_ind), insp['Method'], formatdata)
                                            worksheet2.data_validation('D' + str(insp_ind),
                                                                       {'validate': 'list',
                                                                        'source': '=Lookup!$A$2:$A$37'})
                                            worksheet2.write('E' + str(insp_ind), insp['Coverage'], formatdata)
                                            worksheet2.write('F' + str(insp_ind), insp['Avaiable'], formatdata)
                                            worksheet2.data_validation('F' + str(insp_ind), {'validate': 'list',
                                                                                             'source': ['online',
                                                                                                        'shutdown']})
                                            worksheet2.write('G' + str(insp_ind), insp['Last'], formattime)
                                            worksheet2.write('H' + str(insp_ind), insp['Interval'], formatdata)
                                            worksheet2.write('I' + str(insp_ind), insp['Duedate'], formattime)
                                            insp_ind += 1

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=Report_'+ str(status) + '_[' + str(name) +'].xlsx'
    return response