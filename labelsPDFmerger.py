import argparse
import numpy as np
# configuration
parser = argparse.ArgumentParser(description="Merge F/B PDFs")
parser.add_argument('-s',"--shortname",
                    help="Common identifier for both existing PDFs (labels-template-<shortname>.pdf and labels-template-<shortname>-backsides.pdf")
parser.add_argument('-n',"--npages",
                    help="Number of pages (each)")
parser.add_argument('-a',"--alternating",
                    help="Order the PDFs as front side / back side alternatingly",
                    default='yes')
args = parser.parse_args()

# read in user args
shortname = args.shortname
npages = int(args.npages)
alternating = True if args.alternating == 'yes' else False

if alternating:
    for k in range(npages):
        print('\\includepdf[pages={' + str(k+1) + '}]{labels-template-' + shortname + '.pdf}')
        print('\\includepdf[pages={' + str(k+1) + '}]{labels-template-' + shortname + '-backsides.pdf}')
    
else:
    print('\\includepdf{labels_template-' + shortname + '.pdf}')
    print('\\includepdf{labels_template-' + shortname + '-backsides.pdf}')
