# TagTex
Creating custom nametags, badges with Python + LaTeX( + inkscape).

Here are some infos that worked for me, but they are rather meant as notes and no support is offered.

### 0. Get TagTex:
If you have an ssh-key from your device to GitHub (or select a different option on the repo page).
```shell
git clone git@github.com:AnnikaStein/TagTex.git
cd TagTex
```

### 1. Preparation:
1. Download two (!) .csv files from your competition registration list. [ALWAYS]  
  a) select only the registered competitors (accepted / "bestätigt"), save this as `YOURCOMPETITIONID-registration.csv`, example `RheinlandPfalzOpen2024-registration.csv`  
  b) select ALL people who have ever registered for the competition, including waitlist or deleted registrations, save as for example `YOURCOMPETITIONID-registration-all.csv`, example: `RheinlandPfalzOpen2024-registration-all.csv`

2. Download and extract the WCA database in tsv format. [ALWAYS]  
  place `WCA_export.tsv` in a suitable directory and let the script `main.py` know where to find this information on your device, fill out the hardcoded variable `WCA_database_path` for that purpose.
  
3. You have a competition logo? Use it.  [ALWAYS]  
  the path goes in `main.py` -> `logo_path`.
  
4. Download event-svgs.  [JUST ONCE]  
  put all WCA event-svgs in some folder. The path goes in `main.py` -> `svgs_path`.
  
5. Download QR code for my-comp.  [JUST ONCE]  
  pull the my-comp qr code from the my-comp repo. The path goes in `main.py` -> `qrcode_path`.
  
6. Install required software and config your pdflatex command.  [JUST ONCE]  
  to go from event-svgs to something that LaTeX and hence TagTex understands, you should have inkscape installed on your device. For compiling the doc and performing the conversion in one go, I use `pdflatex -synctex=1 -interaction=nonstopmode --shell-escape whatever.tex`, with texstudio / texlive, this version: `pdfTeX, Version 3.141592653-2.6-1.40.22 (TeX Live 2021) (preloaded format=pdflatex 2021.11.10)`.

### 2. Example usage:
1. Generate the front and back content. [ALWAYS]  
```shell
python main.py -c ../wca-competition-orga/GermanNationals2023-registration -id GermanNationals2023 > output.txt
```
This output can be placed in the template document and will serve as the content to be formatted into printable nametags.
  If you want to sort the nametags alphabetically, just add `-o name` to the script, e.g. you could do
```shell
python main.py -c ../wca-competition-orga/RheinlandPfalzOpen2024-registration -id RheinlandPfalzOpen2024 -o name > outputRLP24.txt
```
(The default is `-o id` which sorts by time of registration, i.e. the WCA Live ID.)
2. Put the front and the back labels into their respective templates. [ALWAYS]  
  there are two templates, using slightly different configs. For each comp, clone them and replace the shortname-placeholder. Inject the output of the previous step via good old copy-paste in both documents respectively.

3. Generate the merged content. [ALWAYS]  
  here is an example to pick pdf pages in a suitable way. Requires a shortname `s`, number of pages of the individual documents `n`, and a flag `a` regarding alternating front/back or grouping all front pages and then all back pages. See an example below.
```shell
python labelsPDFmerger.py -s RLP24 -n 20 -a yes > mergedRLP24.txt
```
4. Compile final merged PDF. [ALWAYS]  
  what you received in the previous step can be placed in the `merged.tex` document, and then, finally, the third and last PDF document is compiled. Happy printing and cutting!
  
### 3. Best practices
- It is advisable to check with a 100% scaled view of the resulting PDF if the size fits with your physical nametags before printing and cutting. The labels package documentation can assist with choosing other dimensions for whitespace on the sheets or a different setup of the grid, and the current example has been tested with 55 x 90 mm tags.
- With Canon MG3600 series printer @ Morbach settings -> duplex mode (flip on long axis), auto-rescale too large pages checkbox is checked

### 4. Used at
- Rheinland-Pfalz Open 2023
- Everstädter Einsteiger Event / Darmstadt Dodecahedron Days 2023
- Kölner Kubing 2023
- German Open 2024
- Rheinland-Pfalz Open 2024

### 5. Annika's thanks go to...
- Sophia Schmoll - wcif api usage and first implementation of the combined front / back (see [phie-dev](https://github.com/AnnikaStein/TagTex/tree/phie-dev) branch for details, using a slightly different approach)
- Malte Ihlefeld - user experience / sorting and usability feedback
- Lion Jäschke - user experience / badge sizing feedback