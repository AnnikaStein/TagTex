import argparse
import requests
import json
import re 
import pycountry
from collections import OrderedDict

# configuration
parser = argparse.ArgumentParser(description="Main script")
parser.add_argument('-c',"--comp_id",
                    help="competition id")
parser.add_argument('-o',"--order_by",
                    help="Order of nametags for printing, options: id, name, default: id",
                    default='id')
parser.add_argument('-od', "--print_orga_delegate",
                    help="print orga and delegate role on nametag, options y, n, default: n",
                    default='n')
args = parser.parse_args()

# read in user args
comp_id = args.comp_id
order_by = args.order_by
print_orga_delegate = args.print_orga_delegate

# get competitor information for specific competition
res = requests.get("https://worldcubeassociation.org/api/v0/competitions/" + comp_id + "/wcif/public")

# if wca page has issues totaly fine to just throw here, not intended to continue in this case
res_json = res.json()
if "error" in res_json:
    print(res_json["error"])
    quit()

# multiple rooms
activities = []
for x in range(len(res_json['schedule']['venues'][0]['rooms'])):
    activities += res_json['schedule']['venues'][0]['rooms'][x]['activities']

activityIdMap = dict()
for activity in activities:
    activityIdMap[activity['id']] = activity['activityCode']
    for child in activity['childActivities']:
        activityIdMap[child['id']] = child['activityCode']
persons = res_json['persons']

if order_by == 'name':
    persons = sorted(persons, key=lambda persons: persons['name'])

# event order
EVENTORDER = ['333', '222', '444', '555', '666', '777', '333bf', '333fm', '333oh', 'clock', 'minx', 'pyram', 'skewb', 'sq1', '444bf', '555bf', '333mbf']

tex_builder = ''
for person in persons:
    # structure {Name}{WCAID}{country}{reg id}{assignments[event & comp & scr & judge & run\\]}
    if (bool((re.compile(r'[\u0400-\u04FF]+')).search(person["name"])) == True): #cyrill letters
        tmpName = '\\foreignlanguage{ukrainian}{' + person["name"] + "}"
    elif (bool((re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')).search(person["name"])) == True): #"chinese"
        tmpName = '\\begin{CJK*}{UTF8}{gbsn}' + person["name"] + '\\end{CJK*}'
    else:
        tmpName = person["name"]
    tex_builder += '\card' + '{' + tmpName + '}'
    tex_builder += '{' + (person["wcaId"], '\\textcolor{ForestGreen}{Newcomer}')[person["wcaId"] == None] + '}'# either wcaId or 'Newcomer'
    tex_builder += '{' + pycountry.countries.get(alpha_2=person["countryIso2"]).name + '}'
    tex_builder += '{' + str(person["registrantId"]) 
    tex_builder += ('' , ('', (' \\textcolor{Red}{' + " ".join(str(x) for x in person["roles"]) + '}'))[person["roles"] != []])[print_orga_delegate == 'y'] + '}'

    assignments = dict()
    for assignment in person['assignments']:
        assignment['activityId'] = activityIdMap[assignment['activityId']]
        
        if (assignment['activityId'].startswith("333fm")):
            pass
        else:
            # acitvityId is build like event-round-group
            # build dict (or whatever; it is python there are no datatypes) 'event' : '[comp,scr,judge,run]' (todo if some assignment type isn't used don't include it)
            activity = assignment['activityId'].split('-') 
            if not(activity[0] in assignments):
                assignments[activity[0]] = [' ',' ',' ',' ']
            if assignment['assignmentCode'] == 'competitor':
                assignments[activity[0]][0] += ((activity[2])[1:], (',' + (activity[2])[1:]))[assignments[activity[0]][0] != ' '] 
            elif assignment['assignmentCode'] == 'staff-scrambler':
                assignments[activity[0]][1] += ((activity[2])[1:], (',' + (activity[2])[1:]))[assignments[activity[0]][1] != ' ']
            elif assignment['assignmentCode'] == 'staff-judge':
                assignments[activity[0]][2] += ((activity[2])[1:], (',' + (activity[2])[1:]))[assignments[activity[0]][2] != ' ']   
            elif assignment['assignmentCode'] == 'staff-run':
                assignments[activity[0]][3] += ((activity[2])[1:], (',' + (activity[2])[1:]))[assignments[activity[0]][3] != ' ']

    # sorting
    assignmentsSorted = OrderedDict((k, assignments[k]) for k in EVENTORDER if k in assignments)
    tex_builder += '{'
    for k in assignmentsSorted:
        tex_builder += k + '&' + str(assignmentsSorted[k][0]) + '&' + str(assignmentsSorted[k][1]) + '&' + str(assignmentsSorted[k][2]) + '&' + str(assignmentsSorted[k][3]) + '\\\\'
    tex_builder += '}'

# writing to tex/content.tex
# overwriting everything, makes no sense if there is already something in
f = open("tex/content.tex", "w")
f.write(tex_builder)
f.close()

#writing comp name
f = open("tex/name.tex", 'w')
f.write(res_json['name'])
f.close()
