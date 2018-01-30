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
            data['apicomponenttypeid'] = api.apicomponenttypename
            data['equipmentType'] = request.POST.get('EquipmentType')

            data['riskperiod']=request.POST.get('RiskAnalysisPeriod')
            if not data['assessmentname']:
                error['assessmentname'] = "Assessment Name does not empty"
            if not data['assessmentdate']:
                error['assessmentdate']= "Assesment Date does not empty!"

            if request.POST.get('adminControlUpset') == "on" or request.POST.get('adminControlUpset') == 1:
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

            if request.POST.get('Downtime') == "on" or request.POST.get('Downtime') == 1:
                downtime = 1
            else:
                downtime = 0
            print( "Down time" + str(downtime) )

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

            rwequipment = RwEquipment(id= rwassessment, commissiondate= data['assessmentdate'], adminupsetmanagement= adminControlUpset, containsdeadlegs= containsDeadlegs,
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

            dm_cal = DM_CAL(APIComponentType= str(data['apicomponenttypeid']),
                 Diametter= float(data['normaldiameter']), NomalThick=float(data['normalthick']), CurrentThick=float(data['currentthick']), MinThickReq=float(data['tmin']), CorrosionRate=float(data['currentrate']), CA=float(data['CA']),
                 ProtectedBarrier= False, CladdingCorrosionRate= float(data['CladdingCorrosionRate']), InternalCladding=bool(InternalCladding), NoINSP_THINNING=1,
                 EFF_THIN="B", OnlineMonitoring=data['OnlineMonitoring'], HighlyEffectDeadleg=bool(HighlyEffe), ContainsDeadlegs=bool(containsDeadlegs),
                 TankMaintain653=False, AdjustmentSettle="", ComponentIsWeld=False,
                 LinningType=data['InternalLinerType'], LINNER_ONLINE=bool(linerOnlineMoniter), LINNER_CONDITION=data['InternalLinerCondition'], YEAR_IN_SERVICE=0, INTERNAL_LINNING=InternalLining,
                 CAUSTIC_INSP_EFF="E", CAUSTIC_INSP_NUM=0, HEAT_TREATMENT=data['heatTreatment'], NaOHConcentration=float(data['NaOHConcentration']), HEAT_TRACE=bool(heatTrace),
                 STEAM_OUT=bool(steamOut),
                 AMINE_INSP_EFF="E", AMINE_INSP_NUM=0, AMINE_EXPOSED=bool(exposureAcid), AMINE_SOLUTION=data['AminSolution'],
                 ENVIRONMENT_H2S_CONTENT=bool(EnvironmentCH2S), AQUEOUS_OPERATOR=bool(aquaDuringOP), AQUEOUS_SHUTDOWN=bool(aquaDuringShutdown), SULPHIDE_INSP_EFF="E",
                 SULPHIDE_INSP_NUM=0, H2SContent= float(data['H2SContent']), PH= float(data['PHWater']), PRESENT_CYANIDE=bool(presentCyanide), BRINNEL_HARDNESS= data['MaxBrinell'],
                 SULFUR_INSP_EFF="E", SULFUR_INSP_NUM=0, SULFUR_CONTENT=data['sulfurContent'],
                 CACBONATE_INSP_EFF="E", CACBONATE_INSP_NUM=0, CO3_CONTENT=float(data['CO3']),
                 PTA_SUSCEP=bool(materialPTA), NICKEL_ALLOY=bool(nickelAlloy), EXPOSED_SULFUR=bool(exposedSulfur), PTA_INSP_EFF="E", PTA_INSP_NUM=0,
                 ExposedSH2OOperation=bool(presentSulphide), ExposedSH2OShutdown=bool(presentSulphidesShutdown), ThermalHistory= data['ThermalHistory'], PTAMaterial= data['PTAMaterialGrade'],
                 DOWNTIME_PROTECTED=bool(downtime),
                 INTERNAL_EXPOSED_FLUID_MIST=bool(materialExposedFluid), EXTERNAL_EXPOSED_FLUID_MIST=bool(materialExposed), CHLORIDE_ION_CONTENT= float(data['ChlorideIon']),
                 CLSCC_INSP_EFF="E", CLSCC_INSP_NUM=0,
                 HSC_HF_INSP_EFF="E", HSC_HF_INSP_NUM=0,
                 HICSOHIC_INSP_EFF="E", HICSOHIC_INSP_NUM=0, HF_PRESENT=bool(presentHF),
                 EXTERNAL_INSP_NUM=0, EXTERNAL_INSP_EFF="E",
                 INTERFACE_SOIL_WATER=bool(interfaceSoilWater), SUPPORT_COATING=bool(supportMaterial), INSULATION_TYPE=data['ExternalInsulationType'], CUI_INSP_NUM=0,
                 CUI_INSP_EFF="E", CUI_INSP_DATE=datetime.now().date(), CUI_PERCENT_1=data['OP1'], CUI_PERCENT_2=data['OP2'],
                 CUI_PERCENT_3=data['OP3'], CUI_PERCENT_4=data['OP4'], CUI_PERCENT_5=data['OP5'], CUI_PERCENT_6=data['OP6'], CUI_PERCENT_7=data['OP7'], CUI_PERCENT_8=data['OP8'],
                 CUI_PERCENT_9=data['OP9'], CUI_PERCENT_10=data['OP10'],
                 EXTERN_CLSCC_INSP_NUM=0, EXTERN_CLSCC_INSP_EFF="E",
                 EXTERNAL_INSULATION=bool(ExternalInsulation), COMPONENT_INSTALL_DATE=datetime.now().date(), CRACK_PRESENT=bool(crackpresent),
                 EXTERNAL_EVIRONMENT=data['ExternalEnvironment'], EXTERN_COAT_QUALITY=data['ExternalCoatingQuality'], EXTERN_CLSCC_CUI_INSP_NUM=0,
                 EXTERN_CLSCC_CUI_INSP_EFF="E", PIPING_COMPLEXITY=data['complex'], INSULATION_CONDITION=data['InsulationCondition'],
                 INSULATION_CHLORIDE= bool(InsulationCholride),
                 MATERIAL_SUSCEP_HTHA=bool(materialHTHA), HTHA_MATERIAL=data['HTHAMaterialGrade'], HTHA_NUM_INSP=0, HTHA_EFFECT="E", HTHA_PRESSURE= float(data['OpHydroPressure'])*0.006895,
                 CRITICAL_TEMP= float(data['criticalTemp']), DAMAGE_FOUND= bool(damageDuringInsp),
                 LOWEST_TEMP=bool(lowestTemp),
                 TEMPER_SUSCEP=bool(suscepTemp), PWHT=bool(pwht), BRITTLE_THICK= float(data['BrittleFacture']), CARBON_ALLOY=bool(cacbonAlloy), DELTA_FATT= float(data['deltafatt']),
                 MAX_OP_TEMP= float(data['maxOT']), CHROMIUM_12= bool(chromium), MIN_OP_TEMP= float(data['minOT']), MIN_DESIGN_TEMP= float(data['minDesignTemp']), REF_TEMP= float(data['tempRef']),
                 AUSTENITIC_STEEL=bool(austeniticStell), PERCENT_SIGMA= float(data['sigmaPhase']),
                 EquipmentType= data['equipmentType'] , PREVIOUS_FAIL= data['prevFailure'], AMOUNT_SHAKING= data['shakingPipe'], TIME_SHAKING=data['timeShakingPipe'], CYLIC_LOAD= data['CylicLoad'],
                 CORRECT_ACTION= data['correctActionMitigate'], NUM_PIPE= data['numberPipe'], PIPE_CONDITION=data['pipeCondition'], JOINT_TYPE= data['joinTypeBranch'], BRANCH_DIAMETER= data['branchDiameter'])

            ca_cal = CA_NORMAL(NominalDiametter = float(data['normaldiameter']), MATERIAL_COST = float(data['materialCostFactor']), FLUID = data['APIFluid'], FLUID_PHASE = data['Systerm'], API_COMPONENT_TYPE_NAME =data['apicomponenttypeid'] , DETECTION_TYPE = data['DetectionType'],
                 ISULATION_TYPE = data['IsulationType'], STORED_PRESSURE = float(data['minOP'])*6.895, ATMOSPHERIC_PRESSURE = 101, STORED_TEMP = float(data['minOT']) + 273, MASS_INVERT = float(data['MassInventory']),
                 MASS_COMPONENT = float(data['MassComponent']), MITIGATION_SYSTEM = data['MittigationSysterm'], TOXIC_PERCENT = float(data['ToxicPercent']), RELEASE_DURATION = data['ReleaseDuration'], PRODUCTION_COST = float(data['ProductionCost']),
                 INJURE_COST = float(data['InjureCost']), ENVIRON_COST = float(data['EnvironmentCost']), PERSON_DENSITY = float(data['PersonDensity']), EQUIPMENT_COST = float(data['EquipmentCost']))

            age ={}
            age['thinning'] = 5.08
            age['linning'] = 5.08
            age['caustics'] = 5.08
            age['amine'] = 5.08
            age['sulphide'] = 5.08
            age['hicsohich2s'] = 5.08
            age['cacbonate'] = 5.08
            age['pta'] = 5.08
            age['clscc'] = 5.08
            age['hschf'] = 5.08
            age['hicsohichf'] = 5.08
            age['externalcorrosion'] = 5.08
            age['cui'] = 5.08
            age['htha'] = 5.08

            print("EXTERNAL_EXPOSED_FLUID_MIST:" + str(dm_cal.EXTERNAL_EXPOSED_FLUID_MIST) + "    " + str(materialExposed))

            DF_SSC_TOTAL_API1 = max(dm_cal.DF_CAUSTIC(age['caustics']), dm_cal.DF_AMINE(age['amine']), dm_cal.DF_SULPHIDE(age['sulphide']), dm_cal.DF_HIC_SOHIC_HF(age['hicsohichf']), dm_cal.DF_HICSOHIC_H2S(age['hicsohich2s']),
                               dm_cal.DF_CACBONATE(age['cacbonate']), dm_cal.DF_PTA(age['pta']), dm_cal.DF_CLSCC(age['clscc']), dm_cal.DF_HSCHF(age['hschf']))

            DF_SSC_TOTAL_API2 = max(dm_cal.DF_CAUSTIC(age['caustics'] + 3), dm_cal.DF_AMINE(age['amine'] + 3),
                               dm_cal.DF_SULPHIDE(age['sulphide'] + 3), dm_cal.DF_HIC_SOHIC_HF(age['hicsohichf'] + 3),
                               dm_cal.DF_HICSOHIC_H2S(age['hicsohich2s'] + 3),
                               dm_cal.DF_CACBONATE(age['cacbonate'] + 3), dm_cal.DF_PTA(age['pta'] + 3),
                               dm_cal.DF_CLSCC(age['clscc'] + 3), dm_cal.DF_HSCHF(age['hschf'] + 3))

            DF_SSC_TOTAL_API3 = max(dm_cal.DF_CAUSTIC(age['caustics'] + 6), dm_cal.DF_AMINE(age['amine'] + 6),
                               dm_cal.DF_SULPHIDE(age['sulphide'] + 6), dm_cal.DF_HIC_SOHIC_HF(age['hicsohichf'] + 6),
                               dm_cal.DF_HICSOHIC_H2S(age['hicsohich2s'] + 6),
                               dm_cal.DF_CACBONATE(age['cacbonate'] + 6), dm_cal.DF_PTA(age['pta'] + 6),
                               dm_cal.DF_CLSCC(age['clscc'] + 6), dm_cal.DF_HSCHF(age['hschf'] + 6))

            DF_EXT_TOTAL_API1 = max(dm_cal.DF_EXTERNAL_CORROSION(age['externalcorrosion']), dm_cal.DF_CUI(age['cui']), dm_cal.DF_EXTERN_CLSCC(), dm_cal.DF_CUI_CLSCC())

            DF_EXT_TOTAL_API2 = max(dm_cal.DF_EXTERNAL_CORROSION(age['externalcorrosion'] + 3), dm_cal.DF_CUI(age['cui'] + 3),
                                    dm_cal.DF_EXTERN_CLSCC(), dm_cal.DF_CUI_CLSCC())
            DF_EXT_TOTAL_API3 = max(dm_cal.DF_EXTERNAL_CORROSION(age['externalcorrosion'] + 6),
                                    dm_cal.DF_CUI(age['cui'] + 6),
                                    dm_cal.DF_EXTERN_CLSCC(), dm_cal.DF_CUI_CLSCC())

            DF_BRIT_TOTAL = max(dm_cal.DF_BRITTLE() + dm_cal.DF_TEMP_EMBRITTLE(), dm_cal.DF_SIGMA(), dm_cal.DF_885())

            DF_HTHA_API1 = dm_cal.DF_HTHA(age['htha'])
            DF_HTHA_API2 = dm_cal.DF_HTHA(age['htha'] + 3)
            DF_HTHA_API3 = dm_cal.DF_HTHA(age['htha'] + 6)

            DF_MFAT = dm_cal.DF_PIPE()

            DF_THINNING_API1 = dm_cal.DF_THIN(age['thinning'])
            DF_THINNING_API2 = dm_cal.DF_THIN(age['thinning'] + 3)
            DF_THINNING_API3 = dm_cal.DF_THIN(age['thinning'] + 6)

            DF_LINNING_API1 = dm_cal.DF_LINNING(age['linning'])
            DF_LINNING_API2 = dm_cal.DF_LINNING(age['linning'] + 3)
            DF_LINNING_API3 = dm_cal.DF_LINNING(age['linning'] + 6)

            if InternalLining and (DF_LINNING_API1 != 0 or DF_LINNING_API2 != 0 or DF_LINNING_API3 != 0):
                DF_THINNING_TOTAL_1 = min(DF_THINNING_API1, DF_LINNING_API1)
                DF_THINNING_TOTAL_2 = min(DF_THINNING_API2, DF_LINNING_API2)
                DF_THINNING_TOTAL_3 = min(DF_THINNING_API3, DF_LINNING_API3)
            else:
                DF_THINNING_TOTAL_1 = DF_THINNING_API1
                DF_THINNING_TOTAL_2 = DF_THINNING_API2
                DF_THINNING_TOTAL_3 = DF_THINNING_API3

            TOTAL_DF_API1 = max(DF_THINNING_TOTAL_1, DF_EXT_TOTAL_API1) + DF_SSC_TOTAL_API1 + DF_HTHA_API1 + DF_BRIT_TOTAL + DF_MFAT
            TOTAL_DF_API2 = max(DF_THINNING_TOTAL_2,DF_EXT_TOTAL_API2) + DF_SSC_TOTAL_API2 + DF_HTHA_API2 + DF_BRIT_TOTAL + DF_MFAT
            TOTAL_DF_API3 = max(DF_THINNING_TOTAL_3,DF_EXT_TOTAL_API3) + DF_SSC_TOTAL_API3 + DF_HTHA_API3 + DF_BRIT_TOTAL + DF_MFAT

            gffTotal = api.gfftotal
            pofap1 = TOTAL_DF_API1 * dataFaci.managementfactor * gffTotal
            pofap2 = TOTAL_DF_API2 * dataFaci.managementfactor * gffTotal
            pofap3 = TOTAL_DF_API3 * dataFaci.managementfactor * gffTotal
            # thinningtype = General or Local
            refullPOF = RwFullPof(id= rwassessment, thinningap1= DF_THINNING_TOTAL_1, thinningap2= DF_THINNING_TOTAL_2, thinningap3= DF_THINNING_TOTAL_3,
                                  sccap1= DF_SSC_TOTAL_API1, sccap2= DF_SSC_TOTAL_API2, sccap3= DF_SSC_TOTAL_API3,
                                  brittleap1=DF_BRIT_TOTAL, brittleap2= DF_BRIT_TOTAL, brittleap3= DF_BRIT_TOTAL,
                                  htha_ap1= DF_HTHA_API1, htha_ap2= DF_HTHA_API2, htha_ap3= DF_HTHA_API3,
                                  fatigueap1= DF_MFAT, fatigueap2= DF_MFAT, fatigueap3= DF_MFAT,
                                  fms= dataFaci.managementfactor, thinningtype="Local",
                                  thinninglocalap1= max(DF_THINNING_TOTAL_1, DF_EXT_TOTAL_API1), thinninglocalap2= max(DF_THINNING_TOTAL_2, DF_EXT_TOTAL_API2), thinninglocalap3= max(DF_THINNING_TOTAL_3, DF_EXT_TOTAL_API3),
                                  thinninggeneralap1= DF_THINNING_TOTAL_1 + DF_EXT_TOTAL_API1, thinninggeneralap2= DF_THINNING_TOTAL_2 + DF_EXT_TOTAL_API2, thinninggeneralap3= DF_THINNING_TOTAL_3 + DF_EXT_TOTAL_API3,
                                  totaldfap1= TOTAL_DF_API1, totaldfap2= TOTAL_DF_API2, totaldfap3= TOTAL_DF_API3,
                                  pofap1= pofap1, pofap2= pofap2, pofap3= pofap3,gfftotal= gffTotal,
                                  pofap1category= dm_cal.PoFCategory(TOTAL_DF_API1), pofap2category= dm_cal.PoFCategory(TOTAL_DF_API2), pofap3category= dm_cal.PoFCategory(TOTAL_DF_API3))

            refullPOF.save()


            calv1 = RwCaLevel1(id= rwassessment, release_phase= ca_cal.GET_RELEASE_PHASE(), fact_di= ca_cal.fact_di(), ca_inj_flame= ca_cal.ca_inj_flame(),
                               ca_inj_toxic= ca_cal.ca_inj_tox(), ca_inj_ntnf= ca_cal.ca_inj_nfnt(),
                               fact_mit= ca_cal.fact_mit(), fact_ait= ca_cal.fact_ait(), ca_cmd= ca_cal.ca_cmd(), fc_cmd= ca_cal.fc_cmd(),
                               fc_affa= ca_cal.fc_affa(), fc_envi= ca_cal.fc_environ(), fc_prod= ca_cal.fc_prod(), fc_inj= ca_cal.fc_inj(),
                               fc_total= ca_cal.fc(), fcof_category= ca_cal.FC_Category(ca_cal.fc()))
            calv1.save()

            refullfc = RwFullFcof(id=rwassessment,fcofvalue= ca_cal.fc(), fcofcategory= ca_cal.FC_Category(ca_cal.fc()), envcost= data['EnvironmentCost'],
                                  equipcost= data['EquipmentCost'], prodcost= data['ProductionCost'], popdens= data['PersonDensity'], injcost= data['InjureCost'])
            refullfc.save()

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