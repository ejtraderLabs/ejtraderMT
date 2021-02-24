
import time
import datetime



# convert datestamp to dia/mes/ano
def convertDate(s):
    return time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())




 #convert timestamp to hour minutes and seconds
def convertTime(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds) 


