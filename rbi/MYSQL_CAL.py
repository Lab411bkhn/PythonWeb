import psycopg2;
from datetime import  datetime;
from dateutil.relativedelta import relativedelta;
import numpy as np;
connect_string = "host='localhost' dbname='djangorbi' user='postgres' password='root'"
#connect_string = "host='ec2-54-217-236-201.eu-west-1.compute.amazonaws.com' dbname='d3s74b7putntgb' user='hphbzavltnvngh' password='971440c9ab2e34c429971d9dc6ce07efbe597516e2e022f20be1a3b76370f69c'"
conn = psycopg2.connect(connect_string)
class MySQL_CAL:
    def GET_TBL_52(fluid):
        row = np.zeros(10);
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT \"MW\",\"Density\",\"NBP\",\"ideal\",\"A\",\"B\",\"C\",\"D\",\"E\",\"Auto\" FROM \"tbl_52_ca_properties_level_1\" WHERE \"Fluid\" = '" + fluid + "'";
            Cursor.execute(sql);
            for r in Cursor:
                row[0] = r[0];
                row[1] = r[1];
                row[2] = r[2];
                row[3] = r[3];
                row[4] = r[4];
                row[5] = r[5];
                row[6] = r[6];
                row[7] = r[7];
                row[8] = r[8];
                row[9] = r[9];
        except psycopg2.InternalError as Error:
            print("Error! execute table 5.2");
        return row;

    def GET_RELEASE_PHASE(fluid):
        data = "Liquid";
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT \"Ambient\" FROM \"tbl_52_ca_properties_level_1\" WHERE \"Fluid\" = '" + fluid + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data = r[0];
        except psycopg2.InternalError as Error:
            print("Error! get Release Phase from table 5.2");
        return data;

    def GET_TBL_58(fluid):
        data = np.zeros(16);
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT * FROM \"tbl_58_ca_component_dm\" WHERE \"Fluid\" = '" + fluid + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data[0] = r[2]
                data[1] = r[3]
                data[2] = r[4]
                data[3] = r[5]
                data[4] = r[6]
                data[5] = r[7]
                data[6] = r[8]
                data[7] = r[9]
                data[8] = r[10]
                data[9] = r[11]
                data[10] = r[12]
                data[11] = r[13]
                data[12] = r[14]
                data[13] = r[15]
                data[14] = r[16]
                data[15] = r[17]
        except psycopg2.InternalError as Error:
            print("Error! execute data from table 5.8 error!");
        return data;

    def GET_TBL_59(fluid):
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        data = np.zeros(16);
        try:
            sql = "SELECT * FROM \"tbl_59_component_damage_person\" WHERE \"Fluid\" = '" + fluid + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data[0] = r[1];
                data[1] = r[2];
                data[2] = r[3];
                data[3] = r[4];
                data[4] = r[5];
                data[5] = r[6];
                data[6] = r[7];
                data[7] = r[8];
                data[8] = r[9];
                data[9] = r[10];
                data[10] = r[11];
                data[11] = r[12];
                data[12] = r[13];
                data[13] = r[14];
                data[14] = r[15];
                data[15] = r[16];
        except psycopg2.InternalError as Error:
            print("Error! Execute data Table 5.9 Fail");
        return data;

    def GET_TBL_213(thickness):
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        data = np.zeros(4);
        try:
            sql = "SELECT * FROM \"tbl_213_dm_impact_exemption\" WHERE \"ComponentThickness\" = '" + str(thickness) + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data[0] = r[1];
                data[1] = r[2];
                data[2] = r[3];
                data[3] = r[4];
        except psycopg2.InternalError as Error:
            print("Error! Execute data from Table 213 Fail");
        return data;

    def GET_TBL_204(susceptibility):
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        data = np.zeros(7);
        try:
            sql = "SELECT * FROM \"tbl_204_dm_htha\" WHERE \"Susceptibility\" = '"+susceptibility+"'";
            Cursor.execute(sql);
            for r in Cursor:
                data[0] = r[2];
                data[1] = r[3];
                data[2] = r[4];
                data[3] = r[5];
                data[4] = r[6];
                data[5] = r[7];
                data[6] = r[8];
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 204 Fail");
        return data;

    def GET_TBL_214(DeltaT, size):
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        data = 0.0;
        try:
            sql = "SELECT \""+str(size)+"\" FROM tbl_214_dm_not_pwht WHERE \"Tmin-Tref\" = '"+str(DeltaT)+"'";
            Cursor.execute(sql);
            for r in Cursor:
                data = r;
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 214 Fail");
        return data;

    def GET_TBL_215(DeltaT, size):
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        data = 0;
        try:
            sql = "SELECT \"" + str(size) + "\" FROM \"tbl_215_dm_pwht\" WHERE \"Tmin-Tref\" = '" + str(DeltaT) + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data = r;
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 215 fail");
        return data;

    def GET_TBL_511(ART, INSP, Effective):
        data = 0;
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            if(Effective == "E"):
                sql = "SELECT \"E\" FROM \"tbl_511_dfb_thin\" WHERE \"art\" ='" + str(ART) + "'";
            else:
                sql = "SELECT \"" + Effective + "\" FROM \"TBL_511_DFB_THIN\" WHERE \"art\" ='" + str(ART) + "' AND \"insp\" = '" + str(INSP) + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data = r;
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 511 Fail");
        return data[0];

    def GET_TBL_512(ART, Effective):
        data = 0;
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT \""+Effective+"\" FROM \"tbl_512_dfb_thin_tank_bottom\" WHERE \"art\" = '"+str(ART)+"'";
            Cursor.execute(sql);
            for r in Cursor:
                data = r;
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 512 fail!");
        return data;

    def GET_TBL_64(YEAR, Suscep):
        data = 0;
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT \"" + Suscep + "\" FROM \"tbl_64_dm_linning_inorganic\" WHERE \"YearsSinceLastInspection\" = '" + str(YEAR) + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data = r;
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 64 fail!");
        return data;

    def GET_TBL_65(YEAR, Suscep):
        data = 0;
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT \"" + Suscep + "\" FROM \"tbl_65_dm_linning_organic\" WHERE \"YearInService\" = '" + str(YEAR) + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data = r;
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 65 fail");
        return data;

    def GET_TBL_74(SVI, field):
        data = 0;
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT \"" + field + "\" FROM \"tbl_74_scc_dm_pwht\" WHERE \"SVI\" ='" + str(SVI) + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data = r;
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 74 fail");
        return data;

    def GET_TBL_3B21(locat):
        data = 0
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT \"SIUnits\" FROM \"tbl_3b21_si_conversion\" WHERE \"conversionFactory\" = '" + str(locat) + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data = r[0];
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 3B21 fail");
        return data;

    def GET_TBL_71_PROPERTIES(FluidTank):
        data = np.zeros(3);
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT \"Molecular Weight\",\"Liquid Density\",\"Liquid Density Viscosity\" FROM \"tbl_71_properties_storage_tank\" WHERE \"Fluid\"='" + FluidTank + "'";
            Cursor.execute(sql);
            for r in Cursor:
                data[0] = r[0];
                data[1] = r[1];
                data[2] = r[2];
        except psycopg2.InternalError as Error:
            print("Error! Execute sql from table 71 fail");
        return data;

    def GET_API_COM(APIComponentTypeName):
        data = np.zeros(13);
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor();
        try:
            sql = "SELECT * FROM \"api_component_type\" WHERE \"APIComponentTypeName\" = '"+str(APIComponentTypeName)+"'";
            Cursor.execute(sql);
            for r in Cursor:
                data[0] = r[2];
                data[1] = r[3];
                data[2] = r[4];
                data[3] = r[5];
                data[4] = r[6];
                data[5] = r[7];
                data[6] = r[8];
                data[7] = r[9];
                data[8] = r[10];
                data[9] = r[11];
                data[10] = r[12];
                data[11] = r[13];
                data[12] = r[14];
        except psycopg2.InternalError as Error:
            print("Error! Execute sql table API_COMPONENT_TYPE fail");
        return data;

    def GET_LAST_INSP(ComponentNumber, DamageName, CommissionDate):
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor()
        try:
            sql = "SELECT MAX(\"InspectionDate\") FROM \"rw_inspection_history\" WHERE \"ComponentNumber\" = '"+str(ComponentNumber)+"' AND \"DM\" = '"+str(DamageName)+"'"
            Cursor.execute(sql)
            data = Cursor.fetchone()
            if data[0] is None:
                date = CommissionDate
            else:
                date = data[0]
        except psycopg2.InternalError as Error:
            print("Error! Excute sql table INSPECTION HISTORY fail")
        return date

    def GET_MAX_INSP(ComponentNumber, DamageName):
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor()
        eff = "E"
        try:
            sql = "SELECT MIN(\"InspectionEffective\") FROM \"rw_inspection_history\" WHERE \"ComponentNumber\" = '"+str(ComponentNumber)+"' AND \"DM\" = '"+str(DamageName)+"'"
            Cursor.execute(sql)
            data = Cursor.fetchone()
            if data[0] is None:
                eff = "E"
            else:
                eff = str(data[0])
        except psycopg2.InternalError as Error:
            print("Error! Excute sql table INSPECTION HISTORY fail")
        return eff

    def GET_NUMBER_INSP(ComponentNumber, DamageName):
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor()
        data=[0]
        try:
            sql = "SELECT COUNT(\"InspectionEffective\") FROM \"rw_inspection_history\" WHERE \"ComponentNumber\" = '"+str(ComponentNumber)+"' AND \"DM\" = '"+str(DamageName)+"'"
            Cursor.execute(sql)
            data = Cursor.fetchone()
        except psycopg2.InternalError as Error:
            print("Error! Excute sql table INSPECTION HISTORY fail")
        return data[0]

    def GET_AGE_INSP(ComponentNumber, DamageName, CommissionDate, AssessmentDate):
        #conn = psycopg2.connect(connect_string)
        Cursor = conn.cursor()
        date = CommissionDate
        try:
            sql = "SELECT MAX(\"InspectionDate\") FROM \"rw_inspection_history\" WHERE \"ComponentNumber\" = '" + str(
                ComponentNumber) + "' AND \"DM\" = '" + str(DamageName) + "'"
            Cursor.execute(sql)
            data = Cursor.fetchone()
            if data[0] is None:
                date = CommissionDate
            else:
                date = data[0]
        except:
            print("Error! get age insp")
        return (AssessmentDate.date() - date.date()).days/365
