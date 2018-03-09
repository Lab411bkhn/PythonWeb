from rbi import Postgresql
import datetime
#abc = Postgresql.POSTGRESQL.GET_LAST_INSP('Vun2','abc', datetime.datetime.now())

abc = Postgresql.POSTGRESQL.GET_AGE_INSP('Vun2','abc', datetime.datetime(2010,2,3), datetime.datetime.now())
print(abc)

