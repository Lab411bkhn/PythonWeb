from operator import eq

from django.shortcuts import render, render_to_response, redirect
from rbi.models import ApiComponentType
from rbi.models import Sites
from rbi.models import Facility,EquipmentMaster, ComponentMaster, EquipmentType, DesignCode, Manufacturer, ComponentType
from rbi.models import FacilityRiskTarget
from django.http import Http404, HttpResponse
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
            error['exist'] = "This Site Existed"
        else:
            if (not data['sitename']):
                error['empty'] = "Sites does not empty!"
            else:
                obj = Sites(sitename= data['sitename'])
                obj.save()
                return redirect('site_display')
    return  render(request,"home/new/newSite.html",{'error': error, 'site': data})

def facility(request,siteid):
    try:
        data = Sites.objects.get(siteid = siteid)
        dataFacility = {}
        error = {}
        if request.method == "POST":
            dataFacility['facilityname'] = request.POST.get('FacilityName')
            dataFacility['siteid'] = siteid
            dataFacility['managefactor'] = request.POST.get('ManagementSystemFactor')
            dataFacility['TargetFC'] = request.POST.get('Financial')
            dataFacility['TargetAC'] = request.POST.get('Area')
            countFaci = Facility.objects.filter(facilityname= dataFacility['facilityname']).count()
            if(not dataFacility['facilityname']):
                error['facilityname'] = "Facility does not empty!"
            if(not dataFacility['managefactor']):
                error['managefactor'] = "Manage Factor does not empty!"
            if(not dataFacility['TargetFC']):
                error['TargetFC'] = "Finance Target does not empty!"
            if(not dataFacility['TargetAC']):
                error['TargetAC'] = "Area Target does not empty!"
            if(dataFacility['facilityname'] and dataFacility['managefactor'] and dataFacility['TargetAC'] and dataFacility['TargetFC']):
                if countFaci == 0:
                    faci = Facility(facilityname= dataFacility['facilityname'],managementfactor= dataFacility['managefactor'], siteid_id=siteid)
                    faci.save()
                    faciOb = Facility.objects.get(facilityname= dataFacility['facilityname'])
                    facility_target = FacilityRiskTarget(facilityid_id= faciOb.facilityid , risktarget_ac= dataFacility['TargetAC'],
                                                         risktarget_fc= dataFacility['TargetFC'])
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
        if request.method == "POST":
            data['equipmentNumber'] = request.POST.get('equipmentNumber')
            data['equipmentName'] = request.POST.get('equipmentName')
            data['equipmentType'] = request.POST.get('equipmentType')
            data['designcode'] = request.POST.get('designCode')
            data['site'] = request.POST.get('Site')
            data['facility'] = request.POST.get('Facility')
            data['manufacture'] = request.POST.get('manufacture')
            data['commisiondate'] = request.POST.get('CommissionDate')
            data['PDFNo'] = request.POST.get('PDFNo')
            data['processDescription'] = request.POST.get('processDescription')
            data['decription']= request.POST.get('decription')
            equip = EquipmentMaster.objects.filter(equipmentnumber= data['equipmentNumber']).count()
            if not data['equipmentNumber']:
                error['equipmentNumber'] = "Equipment Number does not empty!"
            if not data['equipmentName']:
                error['equipmentName'] = "Equipment Name does not empty!"
            if not data['designcode']:
                error['designcode'] = "Design Code does not empty!"
            if not data['manufacture']:
                error['manufacture'] = "Manufacture does not empty!"
            if not data['commisiondate']:
                error['commisiondate'] = "Commission Date does not empty!"
            if (data['equipmentNumber'] and data['equipmentName'] and data['designcode'] and data['manufacture'] and data['commisiondate']):
                if equip > 0:
                    error['exist'] = "Equipment already exists! Please choose other Equipment Number!"
                else:

                    equipdata = EquipmentMaster(equipmentnumber= data['equipmentNumber'], equipmentname= data['equipmentName'], equipmenttypeid_id=EquipmentType.objects.get(equipmenttypename= data['equipmentType']).equipmenttypeid,
                                                designcodeid_id= DesignCode.objects.get(designcode= data['designcode']).designcodeid, siteid_id= Sites.objects.get(sitename= data['site']).siteid, facilityid_id= Facility.objects.get(facilityname= data['facility']).facilityid,
                                                manufacturerid_id= Manufacturer.objects.get(manufacturername= data['manufacture']).manufacturerid, commissiondate= data['commisiondate'], pfdno= data['PDFNo'], processdescription= data['processDescription'], equipmentdesc= data['decription'])
                    equipdata.save()
                    return redirect('equipment_display',facilityname)
    except Facility.DoesNotExist:
        raise Http404
    return render(request,"home/new/equipment.html", {'obj': dataFacility, 'equipmenttype': dataEquipmentType, 'designcode': dataDesignCode, 'manufacture': dataManufacture, 'error': error, 'equipment':data})

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
            data['manufacture'] = request.POST.get('manufacture')
            manufac = Manufacturer.objects.filter(manufacturername= data['manufacture']).count()
            if(manufac > 0):
                error['exist'] = "Manufacture already exists!"
            else:
                if(not data['manufacture']):
                    error['manufacture'] = "Manufacture does not empty!"
                else:
                    manu = Manufacturer(manufacturername= data['manufacture'])
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
        if request.method == "POST":
            data['equipmentNumber'] = request.POST.get('equipmentNub')
            data['equipmentType'] = request.POST.get('equipmentType')
            data['designCode'] = request.POST.get('designCode')
            data['site'] = request.POST.get('plant')
            data['facility'] = request.POST.get('facility')
            data['componentNumer'] = request.POST.get('componentNumer')
            data['componentType'] = request.POST.get('componentType')
            data['apiComponentType'] = request.POST.get('apiComponentType')
            data['componentName'] = request.POST.get('componentName')
            data['comRisk'] = request.POST.get('comRisk')
            data['decription'] = request.POST.get('decription')
            comnum = ComponentMaster.objects.filter(componentnumber= data['componentNumer']).count()
            if(not data['componentNumer']):
                error['componentNumber'] ="Component Number does not empty!"
            if(not data['componentName']):
                error['componentName'] = "Component Name does not empty!"
            if(data['componentNumer'] and data['componentName']):
                if(comnum > 0):
                    error['exist'] = "Component already exists!"
                else:
                    if data['comRisk'] =="on":
                        comRisk = 1
                    else:
                        comRisk = 0
                    com = ComponentMaster(componentnumber= data['componentNumer'], equipmentid_id=EquipmentMaster.objects.get(equipmentnumber= data['equipmentNumber']).equipmentid,
                                          componenttypeid_id= ComponentType.objects.get(componenttypename= data['componentType']).componenttypeid, componentname= data['componentName'],
                                          componentdesc= data['decription'], apicomponenttypeid_id= ApiComponentType.objects.get(apicomponenttypename= data['apiComponentType']).apicomponenttypeid,
                                          isequipmentlinked= comRisk)
                    com.save()
                    return redirect('component_display', equipmentname)
    except EquipmentMaster.DoesNotExist:
        raise Http404
    return render(request,'home/new/component.html', {'obj': dataEq , 'componenttype': dataComponentType, 'api':dataApicomponent})


### Edit function
def editSite(request, sitename):
     try:
        data = Sites.objects.get(siteid= sitename)
     except Sites.DoesNotExist:
         raise Http404
     return render(request,'home/new/newSite.html', {'obj':data});

def editFacility(request, facilityname):
    try:
        data = Facility.objects.get(facilityid= facilityname)
    except Facility.DoesNotExist:
        raise Http404
    return render(request, 'home/new/facility.html', {'obj': data})

def editEquipment(request, equipmentname):
    try:
        data = EquipmentMaster.objects.get(equipmentid= equipmentname)
    except EquipmentMaster.DoesNotExist:
        raise Http404
    return render(request, 'home/new/equipment.html', {'obj':data})

def editComponent(request, componentname):
    try:
        data = ComponentMaster.objects.get(componentid= componentname)
    except ComponentMaster.DoesNotExist:
        raise Http404
    return render(request, 'home/new/component.html', {'obj':data})

def editDesignCode(request, designcodeid):
    try:
        data = DesignCode.objects.get(designcodeid= designcodeid)
    except DesignCode.DoesNotExist:
        raise Http404
    return render(request, 'home/new/newDesignCode.html', {'obj':data})

def editManufacture(request, manufactureid):
    try:
        data = Manufacturer.objects.get(manufacturerid= manufactureid)
    except Manufacturer.DoesNotExist:
        raise Http404
    return render(request, 'home/new/newManufacture.html', {'obj': data})

### Display function
def site_display(request):
    data = Sites.objects.all()
    return render_to_response('display/site_display.html',{'obj':data})

def facilityDisplay(request, sitename):
    try:
        dataSite = Sites.objects.get(siteid= sitename)
        count = Facility.objects.filter(siteid= sitename).count()
        if( count > 1):
            data = Facility.objects.filter(siteid = sitename)
        else:
            data = {}
    except Sites.DoesNotExist:
        raise  Http404
    return  render(request, 'display/facility_display.html', {'obj':data, 'c': sitename})

def equipmentDisplay(request, facilityname):
    try:
        dataFacility = Facility.objects.get(facilityid= facilityname)
        data = EquipmentMaster.objects.filter(facilityid=facilityname)
        siteid = data[0].siteid_id
        facilityid = data[0].facilityid_id
    except Facility.DoesNotExist:
        raise Http404
    return render(request, 'display/equipment_display.html', {'obj':data , 'siteid':siteid, 'facilityid':facilityid})

def componentDisplay(request, equipmentname):
    try:
        dataCom = ComponentMaster.objects.filter(equipmentid= equipmentname)
        dataEq = EquipmentMaster.objects.get(equipmentid= equipmentname)
    except EquipmentMaster.DoesNotExist:
        raise Http404
    return render(request, 'display/component_display.html', {'obj':dataCom, 'equipment': dataEq})

def designcodeDisplay(request, facilityname):
    try:
        dataEq = Facility.objects.get(facilityid= facilityname)
        dataDesign = DesignCode.objects.all()
    except Facility.DoesNotExist:
        raise Http404
    return render(request, 'display/designcode_display.html',{'designcode': dataDesign, 'facilityid': facilityname})

def manufactureDisplay(request, facilityname):
    try:
        dataEq = Facility.objects.get(facilityid= facilityname)
        datamanufacture = Manufacturer.objects.all()
    except Facility.DoesNotExist:
        raise Http404
    return render(request, 'display/manufacture_display.html',{'manufacture': datamanufacture, 'facilityid': facilityname})






