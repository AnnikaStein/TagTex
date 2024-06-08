import argparse
import numpy as np
import pandas as pd
import re
# get remote files with urls
import urllib.request as libreq
# tool to read in the response as json
import json
# for dict sorting business
from collections import OrderedDict
# configuration
parser = argparse.ArgumentParser(description="Main script")
parser.add_argument('-c',"--competitors",
                    help="Path to competitors.csv (without file extension)")
parser.add_argument('-id',"--comp_id",
                    help="Short name of the competition by which one can access the website")
parser.add_argument('-o',"--order_by",
                    help="Order of nametags for printing, options: id, name, default: id",
                    default='id')
args = parser.parse_args()

# read in user args
competitors_path = args.competitors
comp_id = args.comp_id
order_by = args.order_by

# hard-coded stuff
WCA_database_path = '../wca-competition-orga/WCA_export.tsv/'
svgs_path = '/Users/annikastein/github/WCA-German-State-Ranks/assets/event-svg/'
qrcode_path = '/Users/annikastein/github/my-comp/figures/square_qr.png'
logo_path = 'LogoTShirtregular.pdf'

# get competitor information for specific competition
competitors = pd.read_csv(f'{competitors_path}.csv')
competitors_also_deleted = pd.read_csv(f'{competitors_path}-all.csv')

# do not want zero-counting, we are humans and start with * 1 * :-)
competitor_ids = np.array(competitors_also_deleted.loc[competitors_also_deleted.Name.isin(competitors.Name)].index + 1)
competitors['competitor_ids'] = competitor_ids

if order_by == 'name':
    competitors.sort_values(by=['Name'], inplace=True)
    competitors.reset_index(drop=False, inplace=True)

names = competitors['Name']
countries = competitors['Country']
# replace NaN Ids with Str 'Newcomer' for proper printout
competitors['WCA ID'].replace(np.nan, 'Newcomer', inplace=True) # for all views of the column
wca_ids = competitors['WCA ID']
# get competition information (associated staff like organizers and delegates)
competitions = pd.read_csv(f'{WCA_database_path}WCA_export_Competitions.tsv',sep='\t')
this_comp = competitions[competitions['id'] == comp_id]

delegates = this_comp['wcaDelegate']
orga = this_comp['organiser']
comp_name = this_comp['name'].values[0]

# go from a series (pandas) to a list, then split until only names remain
delegates_ = [d for d in delegates]
delegates_ = delegates_[0].split('] [')
delegates_ = [d.split('}{')[0].split('{')[1] for d in delegates_]
orga_ = [o for o in orga]
orga_ = orga_[0].split('] [')
orga_ = [o.split('}{')[0].split('{')[1] for o in orga_]
                          
with libreq.urlopen(f'https://worldcubeassociation.org/api/v0/competitions/{comp_id}/wcif/public') as wcif:
    comp_data = json.load(wcif)

activities = []
for x in range(len(comp_data['schedule']['venues'][0]['rooms'])):
    activities += comp_data['schedule']['venues'][0]['rooms'][x]['activities']

activityIdMap = dict()
for activity in activities:
    activityIdMap[activity['id']] = activity['activityCode']
    for child in activity['childActivities']:
        activityIdMap[child['id']] = child['activityCode']
persons = comp_data['persons']
if order_by == 'name':
    persons = sorted(persons, key=lambda persons: persons['name'])

actual_competitors = []
registrantIds = []
for i,item in enumerate(persons):
    if item['registrantId'] == None:
        # this is the my-mom-is-an-organizer-fix ;-)
        pass
    else:
        actual_competitors.append(item)
        registrantIds.append(item['registrantId'])
#actual_competitors
persons = actual_competitors
# event order
EVENTORDER = ['333', '222', '444', '555', '666', '777', '333bf', '333fm', '333oh', 'clock', 'minx', 'pyram', 'skewb', 'sq1', '444bf', '555bf', '333mbf']

def numeric_order_assignments(a_string):
    if len(a_string) == 0 or a_string == ' ':
        return a_string
    x = a_string.split(',')
    x = [int(k) for k in x]
    x.sort()
    x = ', '.join(map(str, x)) 
    return x
    
# write LaTeX snippet that can be used for labels
for i in range(len(competitor_ids)):
    tex_builder = '\\addresslabel{\\centering{\\vspace{-1em}\\selectlanguage{english} \\hspace{1em} ' + comp_name + '\\qquad \\raisebox{-1.75\\baselineskip}{\\includegraphics[height=4\\baselineskip]{' + logo_path + '}} \\vspace{0.5em} \Huge \\\\ '
    
    country_string = f'{countries[i]}'
    wca_id_string = f'{wca_ids[i]}'
    if wca_id_string == 'Newcomer':
        wca_id_string = '\\textcolor{ForestGreen}{' + wca_id_string + '}'
    competitor_id_string = registrantIds[i]
    
    is_del = True if names[i] in delegates_ else False
    is_orga = True if names[i] in orga_ else False
    optional_role_string = ''
    if is_del and is_orga:
        optional_role_string = 'Delegate, Organizer'
    else:
        if is_del:
            optional_role_string = 'Delegate'
        elif is_orga:
            optional_role_string = 'Organizer'
            
    name_string = f'{names[i]}'
    multi_row_name = False
    if '(' in name_string and ')' in name_string:
        multi_row_name = True
        # this is a name with additional local string with other characters
        # would require a linebreak most likely, so the string is split into two
        # and later the second part is written with a smaller fontsize
        name_string_a, name_string_b = name_string.split('(')
        name_string_a = name_string_a[:-1]
        name_string_b = name_string_b[:-1]
        long_name_smaller_font_start = '{\LARGE '
        long_name_smaller_font_end = '} '
        tex_builder += '\\textbf{\\centering \\begin{minipage}{86mm}\\centering ' + long_name_smaller_font_start + name_string_a + long_name_smaller_font_end + '\\end{minipage}\\vspace{1.5mm}}'
        tex_builder += '}'
        tex_builder += '\\\\'
        if (bool((re.compile(r'[\u0400-\u04FF]+')).search(name_string)) == True):
            tex_builder += ' \\selectlanguage{russian} '
        if (bool((re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')).search(name_string)) == True):
            tex_builder += ' \\begin{CJK*}{UTF8}{gbsn} '
            tex_builder += '(' + name_string_b + ')'
            tex_builder += ' \\end{CJK*}'
        else:
            tex_builder += '(' + name_string_b + ')'
    else:
        long_name_smaller_font_start = '{\LARGE ' if (len(name_string) > 20 or len(optional_role_string) > 0) else '' 
        long_name_smaller_font_end = '} ' if (len(name_string) > 20 or len(optional_role_string) > 0) else '' 
        tex_builder += '\\textbf{\\centering \\begin{minipage}{86mm}\\centering '+ long_name_smaller_font_start + name_string + long_name_smaller_font_end + '\\end{minipage}}}'
    tex_builder += '\\\\ '
    
    
    

    if optional_role_string != '':
        tex_builder += '\\selectlanguage{english} \\ \\\\ ' + '\\textcolor{Red}{' + optional_role_string + '} \\\\ \\vspace{-1em} '
    
    tex_builder += '\\selectlanguage{english} \\begin{tabular}{lcr}	\\qquad &  \\qquad & \\qquad  \\\\' + wca_id_string + '&' + country_string + '& ID: ' + f'{competitor_id_string}' + '\\\\ \\end{tabular}'
    #tex_builder += '\\selectlanguage{english} \\begin{tabular}{lr}	\\qquad &  \\qquad  \\\\' + wca_id_string + '&' + country_string + '\\\\ \\end{tabular}'
    
    tex_builder += '}'
    
    print(tex_builder)

print()
print()
n_persons = len(persons)
print('>>> Number of actual competitors', n_persons)
print('>>> Back side follows...')
print()
print()

def flatten(myList):
    return [x for sub in myList for x in sub]

if n_persons % 2 == 0:
    # no empty filling label needed
    person_slicing = flatten([[2*k+1,2*k] for k in range(n_persons//2)])
else:
    # needs an empty filling label on the second to last position
    person_slicing = flatten([[2*k+1,2*k] for k in range(n_persons//2)]) + [-1, n_persons-1]

for p in person_slicing:
    if p == -1:
        # empty label!
        print('\\addresslabel{\\emptylabel}')
    else:
        person = persons[p]
        if person['registration']['status'] != 'accepted':
            pass
        else:
            tmpName = person["name"]
            assignments = dict()
            for assignment in person['assignments']:
                assignment['activityId'] = activityIdMap[assignment['activityId']]
                if ((assignment['activityId'].startswith("333fm"))):
                    pass
                else:
                    activity = assignment['activityId'].split('-') 
                    if not(activity[0] in assignments):
                        assignments[activity[0]] = [' ',' ',' ',' ']
                    if assignment['assignmentCode'] == 'competitor':
                        assignments[activity[0]][0] += ((activity[2])[1:], (',' + (activity[2])[1:]))[assignments[activity[0]][0] != ' '] 
                    elif assignment['assignmentCode'] == 'staff-scrambler':
                        assignments[activity[0]][1] += ((activity[2])[1:], (',' + (activity[2])[1:]))[assignments[activity[0]][1] != ' ']
                    elif assignment['assignmentCode'] == 'staff-judge':
                        assignments[activity[0]][3] += ((activity[2])[1:], (',' + (activity[2])[1:]))[assignments[activity[0]][3] != ' ']   
                    elif assignment['assignmentCode'] == 'staff-runner':
                        assignments[activity[0]][2] += ((activity[2])[1:], (',' + (activity[2])[1:]))[assignments[activity[0]][2] != ' ']

            # sorting
            assignmentsSorted = OrderedDict((k, assignments[k]) for k in EVENTORDER if k in assignments)


            backside = '\\addresslabel{\\vspace{-1.7em}\\selectlanguage{english}{\\begin{table}[H]\\footnotesize\\hspace{1.1em}\\renewcommand{\\arraystretch}{1.35}'
            if len(assignmentsSorted) > 8:
                # dual-column format
                pass
                backside += '\\begin{tabular}{|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|}\\hline\\rowcolor[HTML]{DAE8FC}{\color[HTML]{000000} Event} & {\color[HTML]{000000} C} & {\color[HTML]{000000} S} &	{\color[HTML]{000000} R} & {\color[HTML]{000000} J} & {\color[HTML]{000000} Event} & {\color[HTML]{000000} C} &	{\color[HTML]{000000} S} & {\color[HTML]{000000} R} & {\color[HTML]{000000} J} \\\\ \\hline'
                n_double = len(assignmentsSorted) - 8
                table_row_counter = 1
                for d in range(n_double):
                    if table_row_counter % 2 == 1:
                        # odd row white
                        backside += '\\rowcolor[HTML]{FFFFFF}'
                    else:
                        # even row light grey
                        backside += '\\rowcolor[HTML]{EFEFEF}'
                    backside += '\\includesvg[height=1em]{' + svgs_path + list(assignmentsSorted.keys())[d] + '.svg}' + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d]][0])) + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d]][1])) + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d]][2])) + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d]][3])) + '&' + '\\includesvg[height=1em]{' + svgs_path + list(assignmentsSorted.keys())[d+8] + '.svg}' + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d+8]][0])) + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d+8]][1])) + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d+8]][2])) + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d+8]][3])) + '\\\\ \\hline'
                    table_row_counter += 1    
                for d in range(n_double,8):
                    if table_row_counter % 2 == 1:
                        # odd row white
                        backside += '\\rowcolor[HTML]{FFFFFF}'
                    else:
                        # even row light grey
                        backside += '\\rowcolor[HTML]{EFEFEF}'
                    backside += '\\includesvg[height=1em]{' + svgs_path + list(assignmentsSorted.keys())[d] + '.svg}' + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d]][0])) + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d]][1])) + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d]][2])) + '&' + numeric_order_assignments(str(assignmentsSorted[list(assignmentsSorted.keys())[d]][3])) + '& & & & & \\\\ \\hline'    
                    table_row_counter += 1
            else:
                # one-column format
                backside += '\\begin{tabular}{|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|>{\\hspace{-0.2em}}c<{\\hspace{-0.2em}}|}\\hline\\rowcolor[HTML]{DAE8FC}{\color[HTML]{000000} Event} & {\color[HTML]{000000} C} & {\color[HTML]{000000} S} &	{\color[HTML]{000000} R} & {\color[HTML]{000000} J} \\\\ \\hline'
                table_row_counter = 1
                for k in assignmentsSorted:
                    if table_row_counter % 2 == 1:
                        # odd row white
                        backside += '\\rowcolor[HTML]{FFFFFF}'
                    else:
                        # even row light grey
                        backside += '\\rowcolor[HTML]{EFEFEF}'
                    backside += '\\includesvg[height=1em]{' + svgs_path + k + '.svg}' + '&' + numeric_order_assignments(str(assignmentsSorted[k][0])) + '&' + numeric_order_assignments(str(assignmentsSorted[k][1])) + '&' + numeric_order_assignments(str(assignmentsSorted[k][2])) + '&' + numeric_order_assignments(str(assignmentsSorted[k][3])) + '\\\\ \\hline'
                    table_row_counter += 1


            backside += '\\end{tabular}\\end{table}}\\vspace{-1.4em}\\selectlanguage{english}\\hspace{1.1em}\\footnotesize\\parbox{27em}{C = Competitor, S = Scrambler, R = Runner, J = Judge.\\\\ The table above shows first rounds only. \\\\ \\ \\\\Please check WCA Live and competitiongroups.com for information about next rounds. Your following assignments will appear there. Your ID: ' + str(person['registrantId']) + '.} \\raisebox{-3.65\\baselineskip}{\\includegraphics[height=7.2\\baselineskip]{' + qrcode_path + '}}}'

            print(backside)