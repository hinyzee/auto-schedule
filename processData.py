
class_abbrev_file = "building_codes.txt"
school_name = "UCSD"

# get all the building codes into a map
f = open(class_abbrev_file)
building_codes = {}
for line in f:
    l = line.split("\t")
    if '(' in l[1]:
        l[1] = l[1].split("(")[0][:-1]
    building_codes[l[0]] = l[1]

# converts 1:03p => (13,03)
def convert_time(i):
    hh, mm = i[:-1].split(':')
    if i[-1] == 'p' and hh != '12':
        hh = str(int(hh) + 12)
    if len(hh) == 1:
        hh = '0' + hh
    return (hh, mm)

# translate the text input of webreg schedule
# into the list of json data that would input to calendar
def webreg_json(text):

    # this dictionary helps us distinguish which webreg event this line is
    trans = {
        "LE":"Lecture", "MI": 'Midterm', "DI": "Discussion",
        "RE": "Review Session", "FI": "Final Exam",
        "SE": "Seminar", "LA": "Lab"
    }

    # this helps translate the webreg dates into google calendar input dates
    weekdays_map = {
        'M':'MO','Tu':'TU','W':'WE','Th':'TH','F':'FR',
        'Sa':'SA','Su':'SU'
    }

    curClass = ""   # current class (lectures and discussions dont have names)
    data = []       # list of data we are returning

    for line in text.split("\n"):
        if line.strip() == '':
            continue
        print("line:",line)
        print("line strip", line.strip())
        x = line.split("\t")
        print("x:",x)
        if len(x) >= 10 and x[3] != "":

            x = x[:11]
            obj = {}

            # get the class title nad description
            obj['description'] = ''
            if x[0] not in ['', ' ']:
                curClass = x[0]
                obj['description'] = "Professor "+x[4]+" teaching "+x[1]
            else:
                x[0] = curClass
            obj['title'] = x[0] + ' '+trans.get(x[3], '\b')

            # location of class
            obj['location'] = ' '.join([ building_codes.get(x[-2], x[-2]), x[-1], ","+school_name ])
            if x[-2] == 'TBA':
                obj['location'] = ''

            # get the start and end times
            startT, endT = x[-3].split("-")
            obj['startH'], obj['startM'] = convert_time(startT)
            obj['endH'], obj['endM'] = convert_time(endT)

            # get the date / week times
            temp = x[7].split()
            if len(temp) == 2:
                obj['date'] = temp[1]
            else:
                for day in weekdays_map:
                    x[7] = x[7].replace(day, weekdays_map[day]+",")
                obj['date'] = x[7][:-1]

            print(obj)

            data.append(obj)

        #elif len(x)>0 and len(x[0])>0 and x[-1][-1]!='\r':
        #    raise ValueError()

    return data



# return '03' when input is 3...
def date_to_str(integer):
    x = str(integer)
    if len(x) == 1:
        x = "0" + x
    return x

# @input (year, month, day, weekday)
# @output (y,m,d,w)
def next_day(today):
    lenMonth = [31,28,31,30,31,30,31,31,30,31,30,31]
    y, m, d, w = today
    dd = d + 1
    mm = m
    yy = y

    # if it's a leap year and it's feb29
    # or if its the end of a normal month
    leap = yy%4==0 and yy%100!=0 and mm==2
    if dd>lenMonth[m-1]+(1 if leap else 0):
        dd = 1
        mm += 1
        if mm > 12:
            mm = 1
            yy += 1

#    print(str(today)+" next "+str((yy,mm,dd,(w+1)%7)))
    return (yy,mm,dd,(w+1)%7)

# determines if today is a holiday
# @input  (year, month, day, weekday)
# @output  True/False
def isHoliday(date):
    # len()==3: the holiday is the (1)st (2)weekday in the (0)th month
    # len()==2: the holiday is on the *1th day of the *0(month)
    holidays = [
        [11, 4, 3], [11, 4, 4],     # thanksgiving (4th thursday and friday)
        [11, 11],                   # veterans day (Nov 11)
        [1, 3, 0],                  # MLK day (3rd Monday of Jan)
        [2, 3, 0],                  # Presidents day
        [5, 4, 0],                  # Memorial day
        [6, 4],                     # july 4th
        [8, 1, 0]                   # labor day
    ]

    y, m, d, w = date
    for hol in holidays:
        if len(hol) == 3 and [m, (d-1)//7+1, w] == hol:
            return True
        if len(hol) == 2 and ( [d, m] == hol or
            (w==0 and [m, d-1] == hol) or
            (w==4 and [m, d+1] == hol)):
            return True
    return False

# returns if date1 <= date2
# @input yyyy-mm-dd
# @output T/F
def AbeforeB(date1, date2):
    y, m, d = (int(x) for x in date1.split("-"))
    ey, em, ed = (int(x) for x in date2.split("-"))
    return y*10000+m*100+d <= ey*10000+em*100+ed;
