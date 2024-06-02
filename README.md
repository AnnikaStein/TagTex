# TagTex
Creating custom nametags, badges. ~~Planning to use~~ Using Python + LaTeX only.

### Preparation:
- you need python
- install dependencies (i would recomend using a virtual enviornment (but up to you to figure out how and if))
```shell
pip install -r requirements.txt
```
- you need latex (texlive for example)
- additional not included in must texlive instalations: [texlive-lang](https://wiki.archlinux.org/title/TeX_Live/CJK)

### Example usage:
```shell
python main.py -c <comp id>
```
Output is stored in tex/content.tex and contains all relevant info for competitor tags. Additional tex/name.tex will be created, only containing comp name.
If you want to sort the nametags alphabetically, just add `-o name` to the script. (The default is `-o id` which sorts by time of registration, i.e. the WCA Live ID.)

In order to get a pdf do
```shell
cd tex
pdflatex lables-tamplate.tex
```
It is advisable to check with a 100% scaled view of the resulting PDF if the size fits with your physical nametags before printing and cutting. The labels package documentation can assist with choosing other dimensions for whitespace on the sheets or a different setup of the grid, and the current example has been tested with 55 x 90 mm tags.

# todo

- duplex drucker
    - welp latex kann das wohl nicht so einfach
- man kann noch über flaggen bei ländern nachdenken
- event symbols
- nicht genutzte assignments
- irgendwie schön comp logos noch reinbasteln (auch optional steuerbar)
- Tag größe über parameter steuern
- tabelle mit assignments von unten nach oben wachsen lassen (weil klammer)
- Comp Logo/WCA Logo integrieren (siehe Wendlingen NameTag)
- Georgisch, Thai Namen suppot (allgemein nochmal schauen was für Zeichensätze es noch gibt, die hier auf Comps auftauchen könnten)
