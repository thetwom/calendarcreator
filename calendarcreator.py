#!/usr/bin/python3

import os
import sys
import subprocess
import random
import calendar
import datetime
from contextlib import contextmanager
from PIL import Image, ExifTags

class CalendarCreator:

    def __init__(self):

        self.days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        self.months = ["Januar", "Februar", "März",
                       "April", "Mai", "Juni", "Juli",
                       "August", "September",
                       "Oktober", "November", "Dezember"]

        self.picoptions = ["vertical", "horizontal", "=", "||", "||="]

        # self.year = datetime.datetime.now().year + 1
        self.texfolder = "texfiles"
        self.calendar_filename = "calendar.pdf"

        self.page_width = 21.0
        self.page_height = 21.0
        self.topmargin = 0.3
        self.bottommargin = 0.3
        self.leftmargin = 0.3
        self.rightmargin = 0.3
        self.overlap = 0.05
        self._show_margin = False
        self._show_margin_line = False
        self.title = None
        self.titlepic = None
        self.titlepos = None
        self.titleanchor = "center"
        self.titleopacity = 0.7
        self.footerheight = 2.0
        self.shiftdict = {}
        self.footer_over_pic = False # overlay footer over picture

        self.citations = 13 * [None]
        self.citation_options = {}

        self.legends = 13 * [None]
        self.legend_options = {}

        self.nweeks_in_line = 3

        self.theme = "light" # "dark"

    def set_shiftdict(self, shiftdict):
        self.shiftdict = shiftdict

    def set_citations(self, citation_list, citation_options={}):
        """Set up citation.

        Args:
            citation_list: List with 13 citations, where the first one is a citation
              for the titlepage, and to following are citations for January, February, ...
              Each list entry must be a dictionary with the following keys,
              (for optional parameters, just leave them out:
              - text: Citation text
              - source  [optional]: Citation source
              - width [optional]: Width of citation in cm  (default=pagewidth/2.5)
              - pos [optional]: List with [x-position, y-position]
                                         (default: [page_width-0.5, footerheight+0.5])
              - anchor [optional]: Anchor where position refers to
                                            (default: "south east"))
              - color: Color of text
              - opacity: Opacity of text
              In order to leave out a citation, use None instead of the dictionary.
            citation_options: General citation options valid for all citations.
              This must be a dictionary which can contain the following keys:
              - fill: Fill color (default: no color)
              - opacity: Opacity level (0.0 - 1.0) for fill color.
              - font size: Latex font size (\small, \large, \Large, ...)
                (default = r"\Large")
              - align: Alignment of text (left, right, center)
        """
        self.citation_options = citation_options

        if len(citation_list) != 13:
            print("Citation list contain exactly 13 entries (title + 12 month)")
            exit(1)
        self.citations = citation_list

    def set_legends(self, legends, legend_options={}):
        """Set legends for titlepage and each month.

        This is basically the same as set_citations.

        Arg:
            legends: See description of citation_list of doc in set_citations().
            legend_options: See description of citation_options of doc in set_citations().
        """

        self.legend_options = legend_options
        if len(legends) != 13:
            print("Legend list contain exactly 13 entries (title + 12 month)")
            exit(1)
        self.legends = legends

    def set_title(self, title=None,pic=None,pos=None,anchor="center",opacity=0.7):
        self.title = title
        self.titlepic = pic
        self.titlepos = pos
        self.titleanchor = anchor
        self.titleopacity = opacity

    def set_page_size(self, width, height):
        self.page_width = width
        self.page_height = height

    def set_margin(self, margin):
        self.topmargin = margin
        self.bottommargin = margin
        self.leftmargin = margin
        self.rightmargin = margin

    def show_margin(self, show_marg=False):
        self._show_margin = show_marg

    def show_margin_line(self, show_line=False):
        self._show_margin_line = show_line

    def get_next_weekday(self, weekday):
        """Return next day of week.

        Args:
            weekday: String of weekday as given in global "days"-list
        Returns:
            Next week name (as given in global "days"-list)
        """
        weekday_idx = self.days.index(weekday) + 1
        if weekday_idx >= len(self.days):
            weekday_idx = 0
        return self.days[weekday_idx]

    def get_previous_month(self, month):
        """Return name of previous month.

        Args:
            month: Name of month as given in the global "months"-list
        Returns:
            Name of previous month as given in globals "months"-list
        """
        month_idx = self.months.index(month) - 1
        if month_idx == -1:
            month_idx = 0
        return self.months[month_idx]

    def create_numbering(self, year, month, nweeks_in_line, page_pos=[0.5,1], anchor="south west"):
        """Create the calender numbering and weekdays.

        Args:
            year: Year used for numbering.
            month: Month name according to global "months"-list for which
               the numbering should be created.
            nweeks_in_line: Number of weeks which should be in one line. E.g. 2 results in
               something like
                         Mo Di Mi Do Fr Sa So Mo Di Mi Do Fr Sa So
                                1  2  3  4  5  6  7  8  9 10 11 12
                         13 14 15 16 ...
            page_pos: List with two value which define the position of the numbering
               on the page (x and y value in cm).
            anchor: Anchor according to latex tikz, of the numbering which should be
               aligned with the page_pos. (e.g. "south west", "center", "north east" ,...)
        Returns:
            Latex string which can be written into a latex file tikzpicture environment to
            create the numbering.
        """
        monthidx = self.months.index(month) + 1
        first_weekday_idx, ndays = calendar.monthrange(year, monthidx)
        firstweekday = self.days[first_weekday_idx]
        print("First weekday of   {}, {}: {}".format(month, year, firstweekday))
        print("Number of days for {}, {}: {}".format(month, year, ndays))

        numstring = r"""  %%% create_numbering:
        \matrix (days) at ({},{}) [
        anchor={},matrix of nodes,nodes={{font=\normalsize}}] {{
        """.format(page_pos[0], page_pos[1], anchor)

        for i in range(nweeks_in_line):
            for d in self.days:
                if d == "So":
                    numstring += r"\color{sunday}"
                else:
                    numstring += r"\color{weekday}"
                numstring += r" \bfseries " + d + " &"
        numstring = numstring[:-1] + r"\\" + "\n"
        numstring += "    "

        firstoffset = self.days.index(firstweekday)

        prev_month = self.get_previous_month(month)
        prev_month_idx = self.months.index(prev_month) + 1
        if prev_month_idx == 12:
            prev_month_year = year -1
        else:
            prev_month_year = year

        tmp, last_day_prev_month = calendar.monthrange(prev_month_year, prev_month_idx)

        weekday = self.days[0]
        pos = 0
        for daynum in range(last_day_prev_month-firstoffset+1, last_day_prev_month+1):
            if weekday == "So":
                numstring += r"\color{sunday!30!footerbackgroundcolor}"
            else:
                numstring += r"\color{weekday!30!footerbackgroundcolor}"
            numstring += " {} &".format(daynum)
            weekday = self.get_next_weekday(weekday)

        pos = firstoffset
        for daynum in range(1,ndays+1):
            if weekday == "So":
                numstring += r"\color{sunday}"
            else:
                numstring += r"\color{weekday}"
            numstring += r" {} &".format(daynum)
            pos += 1
            weekday = self.get_next_weekday(weekday)
            if pos == nweeks_in_line*7:
                numstring = numstring[:-1] + r"\\" + "\n    "
                pos = 0

        for daynum in range(1, nweeks_in_line*7 - pos + 1):
            if weekday == "So":
                numstring += r"\color{sunday!30!footerbackgroundcolor}"
            else:
                numstring += r"\color{weekday!30!footerbackgroundcolor}"
            numstring += " {} &".format(daynum)
            weekday = self.get_next_weekday(weekday)

        numstring += (nweeks_in_line*7 - pos) * " &"
        numstring = numstring[:-1] + r"\\" + "\n"
        numstring += r"  };" + "\n"
        return numstring

    def get_colortheme(self):
        if self.theme == "light":
            themetext = """% color theme
    \colorlet{footerbackgroundcolor}{white}
    \colorlet{sunday}{blue!50!green}
    \colorlet{weekday}{black}
    \colorlet{month}{black} %blue!50!green}
    \colorlet{title}{white}
"""
        elif self.theme == "dark":
            themetext = """% color theme
    \colorlet{footerbackgroundcolor}{black}
    \colorlet{sunday}{blue!50!green}
    \colorlet{weekday}{white}
    \colorlet{month}{white} %blue!50!green}
    \colorlet{title}{white}
"""
        else:
            print("Invalid theme: " + self.theme)
            exit(1)
        return themetext
    
    def get_header(self):
        """Return latex file header.

        Returns:
            String with latex header which can be written to latex file
        """
        headtext = r"""%%% get_header
    \documentclass[tikz]{standalone}

    \usepackage{fontspec}
    \setmainfont[BoldFont=* Bold,Numbers={OldStyle}]{Linux Biolinum O}
    \usepackage{graphicx}
    \usepackage[ngerman]{babel}
    \usepackage{csquotes}
    \usepackage{xcolor}
    \usetikzlibrary{matrix}
""" + self.get_colortheme() + r""" 

    \begin{document}

      \begin{tikzpicture}
    """
        if not self._show_margin:
            tm = 0.0
            bm = 0.0
            rm = 0.0
            lm = 0.0
        else:
            tm = self.topmargin
            bm = self.bottommargin
            rm = self.rightmargin
            lm = self.leftmargin

        headtext += r"  \path [use as bounding box] (0-{lm},0-{bm}) rectangle ({w}+{rm},{h}+{tm});".format(w=self.page_width, h=self.page_height,lm=lm,bm=bm,rm=rm,tm=tm) + "\n\n"

        return headtext

    def get_footer(self):
        """Get closing code of latex file.
        """
        foottext = "\n"
        foottext = "%%% get_footer \n"
        if self._show_margin_line:
            foottext += r"  \draw [green] (0,0) rectangle ({},{});".format(self.page_width, self.page_height) + "\n"
        foottext += """\end{tikzpicture}

    \end{document}
    """
        return foottext

    def create_citation(self, text, options,
                        source="", width=None, pos=None, anchor="south east",
                        color="black", opacity=1):
        """Create latex code for creating a citation.

        Args:
            text: Citation text
            source: Citation source.
            width: Width of citation field in cm
            pos: List with two entries for citation position in cm [x-pos, y-pos]
            anchor: Anchor for pos. (where should we align the citation)
            opacity: Opacity of text (0 - 1)
            color: Color of text
            options: Additional options set by set_citations or set_legends
        Returns:
            latex code for printing the citation
        """
        sourcetext = ""
        if len(source) > 0:
            sourcetext = r"\\ \hfill \emph{{{}}}".format(source)
        if pos is None:
            pos = [self.page_width-0.5, self.footerheight+0.5]
        if width is None:
            width = self.page_width / 2

        fillstring = ""
        if "fill" in options:
            fillstring = fillstring + "fill=" + options["fill"] + ","
        if "opacity" in options:
            fillstring = fillstring + "fill opacity={}".format(
                options["opacity"]) + ","
        if "align" not in options:
            options["align"] = "left"

        citation = "\n"
        citation = "    %%% create_citation\n"
        citation += r"""    \node at ({px},{py}) [
      {filloptions}text opacity={textopacity}, text={textcolor}, align={align},text width={w}cm,font={font size},
      rounded corners=1.5mm,anchor={an}] {{
        {tx} {srt}
    }};
""".format(px=pos[0], py=pos[1], w=width, an=anchor, tx=text, srt=sourcetext,
           filloptions=fillstring, textopacity=opacity, textcolor=color, **options)

        return citation

    def get_image_size_and_rotation(self, picname):
        """Find out the size and rotation of the picture.

        Args:
            picname: Filename of picture
        Returns:
            size in pixels as list [width, height], rotation in degree (0, 90, 180 or 270)
        """
        orientmap = {}
        orientmap[3] = 180
        orientmap[Image.ROTATE_270] = 270
        orientmap[Image.ROTATE_90] = 90
        for ori in ExifTags.TAGS.keys():
            if ExifTags.TAGS[ori]=='Orientation':
                break

        im = Image.open(picname)

        imsize = [im.size[0], im.size[1]]

        try:
            exif=dict(im._getexif().items())
            orientation = exif[ori]
        except (KeyError, AttributeError):
            orientation = "blub"

        if orientation == 3:
            return imsize, 180
        elif orientation == 6:
            imsize.reverse()
            return imsize, 270
        elif orientation == 8:
            imsize.reverse()
            return imsize, 90
        else:
            return imsize, 0

    def get_pic(self, picname, center, width, height, lmargin, rmargin, tmargin, bmargin, shift):
        """Create latex string to include a picture on the calender page.

        Args:
            picname: Name of picture which should be included. Note that the path must be given based on
               where this function is called. (If we call some function like openpicture(picname), this should
               be able to open the picture)
            center: Center of picture in cm given as a list [x position, y position].
            width: Picture width in cm (picture will then span from xcenter-width/2 to xcenter+width/2)
            heigth: Picture hwidht in cm (picture will then span from ycenter-height/2 to ycenter+height/2)
            lmargin: Increase the picture size on the left by this value (cm)
            rmargin: Increase the picture size on the right by this value (cm)
            tmargin: Increase the picture size at the top by this value (cm)
            bmargin: Increase the picture size at the bottom by this value (cm)
            shift: Value from -1.0 to 1.0.
               If the given picture is wider than necessary, 0.0 will show the center of the picture, -1.0 will shift
               it to the most left and 1.0 will shift it to the most right. Any values inbetween will shift
               proportially to left or right.
               If the picture is higher than necessary, 0.0 will show the center of the picture, -1.0 will shift to
               down as much as possible, 1.0 will shift up as much as possible. Values inbetween whill shift
               proportiaonlly down or up.
        Returns:
            Picture code, which is written to a latexfile (latex file should be in texfolder to match the picture path)x
        """

        # Find relative path of picture based on latex folder
        abs_pic_path = os.path.dirname(os.path.abspath(picname))
        abs_latex_path = os.path.abspath(self.texfolder)
        rel_picpath_latex = os.path.relpath(abs_pic_path, abs_latex_path)
        pic_latex = rel_picpath_latex + os.sep + os.path.basename(picname)

        imsize, rotate = self.get_image_size_and_rotation(picname)

        # Find picture width, height and position
        totwidth = width+lmargin+rmargin
        totheight = height+tmargin+bmargin

        targetaspect = totwidth / totheight
        pictureaspect = float(imsize[0]) / float(imsize[1])

        #widthratio = float(imsize[0]) / totwidth
        #heightratio = float(imsize[1]) / totheight

        pic_center = [
            center[0] + (rmargin-lmargin)/2.0,
            center[1] + (tmargin-bmargin)/2.0
        ]

        hshift = 0
        vshift = 0

        #if heightratio < widthratio:
        if targetaspect < pictureaspect:
            incstring = "totalheight={}cm".format(totheight)
            picwidth = imsize[0] / float(imsize[1]) * float(totheight)
            #hshift = shift * picwidth
            hshift = shift * 0.5 * (picwidth - totwidth)
        else:
            incstring = "width={}cm".format(totwidth)
            picheight = imsize[1] / float(imsize[0]) * float(totwidth)
            #vshift = shift * picheight
            vshift = shift * 0.5 * (picheight - totheight)

        # Get latex code for clipping the picture
        pc = "  %%% get_pic\n"
        pc = r"  \begin{scope}" + "\n"
        pc += r"     \path [clip] ({},{}) rectangle ({},{});".format(
            center[0]-width/2.0-lmargin, center[1]-height/2.0-bmargin,
            center[0]+width/2.0+rmargin, center[1]+height/2.0+tmargin)
        pc += "\n"

        # Get latex code for writing the picture
        pc += r"    \node at ({},{}) [anchor=center,inner sep=0,outer sep=0] {{".format(pic_center[0]+hshift, pic_center[1]+vshift) + "\n"
        #pc += r"      \includegraphics[width={}cm]{{{}}}".format(picwidth, picname) + "\n"
        if rotate == 0:
            pc += r"      \includegraphics[{}]{{{}}}".format(incstring, pic_latex) + "\n"
        elif rotate == 90 or rotate == 270:
            pc += r"      \includegraphics[angle={},{}]{{{}}}".format(rotate, incstring, pic_latex) + "\n"
        elif rotate == 180:  ## done separately to avoid latex error ...
            pc += r"      \includegraphics[{},angle={}]{{{}}}".format(incstring, rotate, pic_latex) + "\n"
        else:
            print("invalid rotation")
            exit(1)
        pc += r"    };" + "\n"
        pc += r"  \end{scope}" + "\n"
        return pc


    def get_monthtext(self, month, year, page_pos=None, anchor="south east"):
        """Get latex text for writing month to calendar page.

        Args:
            month: Month name to be written
            page_pos: List with two value which define the position of the month text
               on the page (x and y value in cm). If None we use [page_width-0.2,0]
            anchor: Anchor according to latex tikz, of the month text which should be
               aligned with the page_pos. (e.g. "south west", "center", "north east" ,...)
        """
        if page_pos is None:
            page_pos = [self.page_width-0.2, 0]
        monthtext = month + " " + str(year)
        ms = "  %%% get_monthtext\n"
        ms += r"  \node at ({},{}) [anchor={},font=\scshape,color=month!70!footerbackgroundcolor,scale=4,inner sep=0, outer sep=0] {{{}}};".format(
            page_pos[0],  page_pos[1], anchor, monthtext) + "\n\n"
        return ms

    def create_page(self, year, month, pics):
        """Create latex text for a complete calendar page with four pictures and the
        numbering at the bottom.

        The files will be created inside "texfolder". The name is xx_monthname.tex where xx is
        01, 02, 03, ... depending on the month and monthname is the month name given.

        At the end lualatex will be called on the created file.

        Args:
            year: Year of the month to be created
            month: Month name according to the global "months"-list for which the page should be created
            pics: List with four pictures to be placed on the page. Path of the pictures must be
               relative to the current path where this function is called.

        Returns: pdf filename of calendar page.
        """
        midx = self.months.index(month) + 1
        filename = "{:02d}_{}.tex".format(midx,month)
        outfile = self.texfolder + os.sep + filename

        if self.footer_over_pic:
            pic_height = self.page_height
            bottommargin = self.bottommargin
        else:
            pic_height = self.page_height - self.footerheight
            bottommargin = 0

        shifts = self.get_shift(pics)

        pics_optionless = []
        if type(pics) is list:
            for p in pics:
                if p not in self.picoptions:
                    pics_optionless.append(p)
        else:
            pics_optionless = pics

        # print(pics)
        with open(outfile,"w") as f:
            f.write(self.get_header())
            #f.write(get_pics("pic1", "pic2", "pic3", "pic4"))

            if pics is None:
                pass

            ## One picture
            elif type(pics) is not list:
                f.write(self.get_pic(pics, [self.page_width/2.0,self.page_height-pic_height/2.0], self.page_width, pic_height, self.leftmargin, self.rightmargin, self.topmargin, bottommargin, shifts))

            elif "vertical" in pics or "||" in pics:
                num_pics = len(pics_optionless)
                pic_width = self.page_width / num_pics
                for i in range(num_pics):
                    if i == 0:
                        left_margin_pic = self.leftmargin
                    else:
                        left_margin_pic = 0.0

                    if i == num_pics - 1:
                        right_margin_pic = self.rightmargin
                    else:
                        right_margin_pic = self.overlap

                    f.write(self.get_pic(pics_optionless[i], [pic_width * (i + 0.5), self.page_height-pic_height/2.0], pic_width, pic_height, left_margin_pic, right_margin_pic, self.topmargin, bottommargin, shifts[i]))

            elif "horizontal" in pics or "=" in pics:
                num_pics = len(pics_optionless)
                single_pic_height = pic_height / num_pics
                for i in range(num_pics):
                    if i == 0:
                        top_margin_pic = self.topmargin
                    else:
                        top_margin_pic = 0.0

                    if i == num_pics - 1:
                        bottom_margin_pic = self.bottommargin
                    else:
                        bottom_margin_pic = self.overlap
                    f.write(self.get_pic(pics_optionless[i], [self.page_width/2.0,self.page_height-single_pic_height * (i + 0.5)], self.page_width, single_pic_height, self.leftmargin, self.rightmargin, top_margin_pic, bottom_margin_pic, shifts[i]))

            elif len(pics_optionless) == 4 and "||=" in pics:
                width_h = 0.45 * self.page_width
                width_v = (self.page_width - width_h) / 2
                height_h = pic_height / 2
                height_v = pic_height
                # first vertical
                f.write(self.get_pic(pics_optionless[0], [width_v / 2,self.page_height - 0.5 * pic_height], width_v, height_v, self.leftmargin, self.overlap, self.topmargin, self.bottommargin, shifts[0]))
                # second vertical
                f.write(self.get_pic(pics_optionless[1], [width_v * 3 / 2,self.page_height - 0.5 * pic_height], width_v, height_v, 0, self.overlap, self.topmargin, self.bottommargin, shifts[1]))
                # first horizontal
                f.write(self.get_pic(pics_optionless[2], [2*width_v + width_h/2,self.page_height - pic_height / 4], width_h, height_h, 0, self.rightmargin, self.topmargin, self.overlap, shifts[2]))
                # second horizontal
                f.write(self.get_pic(pics_optionless[3], [2*width_v + width_h/2,self.page_height - pic_height * 3.0 / 4.0], width_h, height_h, 0, self.rightmargin, 0, self.bottommargin, shifts[3]))
         
            ## Four pictures
            elif len(pics) == 4:
                # north west pic
                f.write(self.get_pic(pics[0], [self.page_width/4.0,self.page_height-pic_height/4.0], self.page_width/2.0, pic_height/2.0, self.leftmargin, self.overlap, self.topmargin, self.overlap, shifts[0]))

                # north east pic
                f.write(self.get_pic(pics[1], [3.0*self.page_width/4.0,self.page_height-pic_height/4.0], self.page_width/2.0, pic_height/2.0, 0.0, self.rightmargin, self.topmargin, self.overlap, shifts[1]))

                # south west pic
                f.write(self.get_pic(pics[2], [self.page_width/4.0,self.page_height-3.0*pic_height/4.0], self.page_width/2.0, pic_height/2.0, self.leftmargin, self.overlap, 0.0, bottommargin, shifts[2]))

                # south east pic
                f.write(self.get_pic(pics[3], [3.0*self.page_width/4.0,self.page_height-3.0*pic_height/4.0], self.page_width/2.0, pic_height/2.0, 0.0, self.rightmargin, 0.0, bottommargin, shifts[3]))
            else:
                print("Currently only a single pic or a list of four pics can be put on one page")
                exit(1)

            if self.footer_over_pic:
                f.write(r"\fill [footerbackgroundcolor, opacity=0.7] ({},{}) rectangle ({},{});".format(-self.leftmargin, -self.bottommargin, self.page_width+self.rightmargin, self.footerheight) + "\n")

            cit = self.citations[midx]
            if cit is not None:
                f.write(self.create_citation(**cit, options=self.citation_options))

            leg = self.legends[midx]
            if leg is not None:
                f.write(self.create_citation(**leg, options=self.legend_options))

            f.write(self.create_numbering(year, month, self.nweeks_in_line, [0.7,0], "south west"))
            f.write(self.get_monthtext(month, year, [self.page_width-0.2,0], "south east"))

            f.write(self.get_footer())

        with cd(self.texfolder):
            subprocess.call(["lualatex",  filename],stdout=open(os.devnull, 'wb'))
        return self.texfolder + os.sep + filename.replace(".tex",".pdf")


    def create_titlepage(self, year):
        """Create latex text for the calendar title page with one picture.

        The latex file will be created inside "texfolder". The name is 00_titlepage.tex.

        At the end lualatex will be called on the created file.

        Returns: pdf filename of titlepage
        """
        filename = "00_titlepage.tex"
        outname = self.texfolder + os.sep + filename
        # titlename = r"Selfie-Kalender \\ {}".format(year)

        #footerheight = 2
        #pic_height = pageheight+margin - footerheight
        #pic_width = pagewidth + 2*margin

        #pic_height = pageheight/2.0
        #pic_width = pagewidth/2.0

        pic_height = self.page_height + self.topmargin + self.bottommargin
        pic_width = self.page_width + self.leftmargin + self.rightmargin

        center = []
        center.append(self.page_width / 2.0)
        #center.append(pageheight+margin - pic_height/2.0)
        center.append(self.page_height / 2.0)

        if self.title is None:
            tname = "Kalendar {}".format(year)
        else:
            tname = self.title

        if self.titlepos is None:
            self.titlepos = [self.page_width/2.0, self.page_height/2.0]

        with open(outname, "w") as f:
            f.write(self.get_header())
            if self.titlepic is not None:
                f.write(self.get_pic(self.titlepic, center, pic_width, pic_height,
                                     self.leftmargin, self.rightmargin, self.topmargin, 0,
                                     self.get_shift(self.titlepic)))

            f.write(r"\node at ({},{}) [anchor={},font=\scshape,color=title,scale=4,inner sep=0, outer sep=0,align=center, text opacity={}] {{{}}};".format(
                self.titlepos[0], self.titlepos[1], self.titleanchor, self.titleopacity, tname) + "\n\n")
            #f.write(r"\node at ({},{}) [anchor=south east,font=\scshape,color=month!70,scale=4,inner sep=0, outer sep=0] {{{}}};".format(
            #    pagewidth,  0, titlename) + "\n\n")
            #f.write(r"\node at ({},{}) [anchor=south,font=\scshape,color=month!70,scale=4,inner sep=0, outer sep=0] {{{}}};".format(
            #    pagewidth/2.0, 4.0/5.0*pageheight, titlename) + "\n\n")

            cit = self.citations[0]
            print(cit)
            if cit is not None:
                f.write(self.create_citation(**cit, options=self.citation_options))
            leg = self.legends[0]
            if leg is not None:
                f.write(self.create_citation(**leg, options=self.legend_options))

            f.write(self.get_footer())

        with cd(self.texfolder):
            subprocess.call(["lualatex",  filename],stdout=open(os.devnull, 'wb'))
        return self.texfolder + os.sep + filename.replace(".tex", ".pdf")

    def join_pages(self, pages, filename):
        """Join calender pages to one big file.

        Args:
            pages: List with PDF filenames for pages which should be joined
            filename: Filename of joined calendar
        """
        subprocess.call(["pdfunite"] + pages + [filename])

    def create_calendar(self, pics, year_start, month_start):
        """Main function which will create a whole calendar.

        Args:
            pics: One picture or four pictures for each month
               - either a list of 12 pictures
                 (or any other number for more or less months)
               - or a list with 12 lists of four pictures
                 (or any other number for more or less months)
            year_start: Year of first month in calender
            month_start: Index of first month (1 -> January, 2 -> February, ...)
        """
        filenames = []

        if not os.path.exists(self.texfolder):
            os.mkdir(self.texfolder)

        fn = self.create_titlepage(year_start)
        filenames.append(fn)

        num_months = len(pics)
        year = year_start
        imonth = month_start
        #for i, month in enumerate(self.months):
        for i in range(num_months):
            while imonth > 12:
                imonth = imonth - 12
                year = year + 1
            month = self.months[imonth-1]
            print("Generating " + month)
            if pics is None:
                monthpics = None
            else:
                monthpics = pics[i]
            fn = self.create_page(year, month, monthpics)
            filenames.append(fn)

            imonth = imonth + 1
        print("Merging files to " + self.calendar_filename)
        self.join_pages(filenames, self.calendar_filename)

    def get_shift(self, picname):
        """Get shifts of one picture or a picture list

        Args:
            picname: Name of one picture or list of several pictures

        Returns:
            Value given in shiftdict for each given picture. If shiftdict
            does not have a value for the given picture(s) we use the value 0.
        """

        if picname is None:
            return None
        elif type(picname) is list:
            shft = []
            for pn in picname:
                if pn in self.picoptions:
                    pass
                elif pn in self.shiftdict:
                    shft.append(float(self.shiftdict[pn]))
                else:
                    shft.append(float(0))
            return shft
        else :
            if picname in self.shiftdict:
                return float(self.shiftdict[picname])
            else:
                return float(0)

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
