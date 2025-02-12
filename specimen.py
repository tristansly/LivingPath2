import utils

def save(path, fullName=" ", ext=" ", name=" ", title=" ", txt=" ", fst=" "):

    destPath = utils.path( str(utils.path_dir(path))+'/'+str(utils.path_name(path))+'_specimen.html' )
    htmlPath = utils.path('files/specimen.html')
    cssPath = utils.path('files/specimen.css')

    with open(htmlPath,'r',encoding="utf-8") as htmlFile, open(cssPath,'r',encoding="utf-8") as cssFile, open(destPath,'w',encoding="utf-8") as saveFile :

        ext = ext.lower()
        html, css = htmlFile.read(), cssFile.read()
        format = 'opentype'
        if "ttf" in ext : format = 'truetype'
        if "woff" in ext : format = 'woff'
        if "woff2" in ext : format = 'woff2'

        for i, j in {'{{css}}':css, '{{fullName}}':fullName,'{{ext}}':ext,'{{format}}':format,'{{name}}':name,'{{title}}':title,'{{txt}}':txt,'{{fst}}':fst }.items():
            html = html.replace(i, j)

        saveFile.write(html)





#------------------------------------------------------------------------------------------#
