import os
from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'rbi.settings'
application = get_wsgi_application()

from rbi import models
import xlsxwriter

workbook = xlsxwriter.Workbook('report.xlsx')
worksheet = workbook.add_worksheet('Risk Summary')
worksheet1 = workbook.add_worksheet('Risk Summry Detail')
worksheet2 = workbook.add_worksheet('Inspection Plan')

format = workbook.add_format()
format.set_font_name('Times New Roman')
format.set_font_size(14)
format.set_border()
format.set_rotation(90)
format.set_align('center')

format1 = workbook.add_format()
format1.set_font_name('Times New Roman')
format1.set_font_size(14)
format1.set_border()
format1.set_align('center')

formatdata = workbook.add_format()
formatdata.set_font_name('Times New Roman')
formatdata.set_font_size(14)

### SHEET CONTENT
### sheet 1 RiskSummary Ban Tho
worksheet.merge_range('A1:D1', 'Indentification', format1)
worksheet.set_column('C2:C2', 30)
worksheet.set_column('B2:B2', 5)
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
worksheet1.set_column('C2:C2', 30)
worksheet1.set_column('B2:B2', 5)
worksheet1.write('A2', 'Equipment', format)
worksheet1.write('B2', 'Equipment Description', format)
worksheet1.write('C2', 'Equipment Type', format)
worksheet1.write('D2', 'Components', format)
worksheet1.merge_range('E1:E2', 'Represent.fluid', format)
worksheet1.merge_range('F1:F2', 'Fluid phase', format)
worksheet1.merge_range('G1:M1', 'Consequence (COF)', format1)
worksheet1.merge_range('O1:W1', 'Probability (POF)', format1)
worksheet1.merge_range('X1:Y1', 'Risk', format1)
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
data = models.RwFullPof.objects.filter(id= 68)
data1 = models.RwCaLevel1.objects.filter(id= 68)
index = range(0,data.count())

zipRisk = zip(data, data1, index)
for a,b,ind in zipRisk:
    i = 3 + ind
    htha = a.htha_ap1 + a.htha_ap2
    worksheet.write('O' + str(i), a.thinningap1,formatdata)
    worksheet.write('P' + str(i), a.sccap1,formatdata)
    worksheet.write('Q' + str(i), htha,formatdata)
    initPoF = a.thinningap1 + a.sccap1 + a.htha_ap1 + a.htha_ap2
    worksheet.write('R' + str(i), initPoF,formatdata)
    worksheet.write('S' + str(i), a.externalap1,formatdata)
    worksheet.write('T' + str(i), 0,formatdata)
    worksheet.write('U' + str(i), 0,formatdata)
    extPoF = a.externalap1
    worksheet.write('V' + str(i), extPoF,formatdata)
    #PoF = initPoF + extPoF
    worksheet.write('W' + str(i), a.totaldfap1,formatdata)
    worksheet.write('G' + str(i), 0,formatdata)
    worksheet.write('H' + str(i), b.ca_inj_flame,formatdata)
    worksheet.write('I' + str(i), b.fc_inj,formatdata)
    worksheet.write('J' + str(i), b.fc_prod,formatdata)
    worksheet.write('K' + str(i), b.fc_envi,formatdata)
    worksheet.write('L' + str(i), 0,formatdata)
    worksheet.write('M' + str(i), b.fc_total,formatdata)
    z = a.pofap1 * b.fc_total
    k = a.pofap2 * b.fc_total
    worksheet.write('X' + str(i), z,formatdata)
    worksheet.write('Y' + str(i), k,formatdata)

data2 = models.RwInputCaLevel1.objects.all()
index2 = range(0, data2.count() - 1)
zipData2 = zip(data2, index2)
for c, index2 in zipData2:
     i = 3 + index2
     worksheet.write('E' + str(i), c.api_fluid)
     worksheet.write('F' + str(i), c.system)

workbook.close()