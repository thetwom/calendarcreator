import calendarcreator
import random
import os

def create_pic_list(picfolder):
    pics = 12 * [None]
    pics[0] = picfolder + os.sep + "p01.jpg"
    pics[1] = picfolder + os.sep + "p02.jpg"
    pics[2] = [picfolder + os.sep + "p03.jpg",
               picfolder + os.sep + "p04.jpg",
               picfolder + os.sep + "p05.jpg",
               picfolder + os.sep + "p06.jpg"]
    pics[3] = [picfolder + os.sep + "p07.jpg",
               picfolder + os.sep + "p08.jpg",
               picfolder + os.sep + "p09.jpg",
               picfolder + os.sep + "p10.jpg"]
    pics[4] = [
        picfolder + os.sep + "p11.jpg",
        picfolder + os.sep + "p12.jpg",
        "vertical"
    ]
    pics[5] = [
        picfolder + os.sep + "p13.jpg",
        picfolder + os.sep + "p14.jpg",
        "vertical"
    ]
    pics[6] = [
        picfolder + os.sep + "p15.jpg",
        picfolder + os.sep + "p16.jpg",
        "vertical"
    ]
    pics[7] = [
        picfolder + os.sep + "p17.jpg",
        picfolder + os.sep + "p18.jpg",
        "horizontal"
    ]
    pics[8] = [
        picfolder + os.sep + "p19.jpg",
        picfolder + os.sep + "p20.jpg",
        "horizontal"
    ]
    pics[9] = None
    pics[10] = picfolder + os.sep + "p20.jpg"
    pics[11] = picfolder + os.sep + "p21.jpg"

    return pics


def get_shift_dictionary(picfolder):
    shifts = {}
    shifts["p01.jpg"] = 0.5
    shifts["p03.jpg"] = 0.4
    shifts["p05.jpg"] = 0.5
    shifts["p06.jpg"] = 0.4
    shifts["p07.jpg"] = -0.5
    shifts["p08.jpg"] = 0.0
    shifts["p09.jpg"] = 0.2
    shifts["p12.jpg"] = 0.5
    shifts_with_folder = {}
    for key, val in shifts.items():
        shifts_with_folder[picfolder+os.sep+key] = val

    return shifts_with_folder

def get_citations():

    citations = [
        # title
        None,
        # January
        {"text" : "see this nice picture",
         "source" : "nobody",
         "pos" : [22.0,2.5],
         "width" : 5,
         "anchor" : "south east"
        },
        # February
        None,
        # March
        {"text" : "something",
         "source" : "also nobody",
         "pos" : [22.0,2.5],
         "width" : 5,
         "anchor" : "south east"
        },
        # April
        None,
        # May
        None,
        # June
        None,
        # July
        None,
        # August
        None,
        # September
        None,
        # October
        None,
        # November
        None,
        # December
        None,
    ]

    return citations

def get_legends(pagewidth):

    legends = [
        {"text" : r"my first legend",
         "width" : 15,
         "pos" : [pagewidth-0.2,0.1],
         "anchor" : "south east",
         "opacity" : 0.5,
         "color" : "white"
        }
    ]

    colors = ["white", "black", "white", "white", "white", "white", "black", "white",
              "white", "white", "white", "white"]
    names = ["l1", "a legend", "another legend", "whatever",
            "something", "hi ", "not sure",
            "someone", "someone else", "great", "abc",
            "efg"]
    for c, n in zip(colors, names):
        legends.append(
            {"text" : n + r"\,\textcopyright\,Me, 2022",
             "width" : 15,
             "pos" : [pagewidth-0.2,2.0],
             "anchor" : "south east",
             "opacity" : 0.5,
             "color" : c
            }
        )
    return legends


if __name__ == "__main__":

    picfolder = "pictures"
    pics = create_pic_list(picfolder)
    shift_dict = get_shift_dictionary(picfolder)
    pagewidth = 23 # cm
    pageheight = 17 # cm

    margin = 0.3 # cm
    show_margin = False
    show_margin_lines = False

    year_start = 2023
    month_start = 1

    titlepic = picfolder + os.sep + "p22.jpg"
    titlename = r"Calendar {}".format(year_start)
    titlepos = [0.9, pageheight/2.0]
    titleanchor = "north west"

    citation_options = {
        "fill":"white",
        "opacity":0.7,
        "font size":r"\normalsize"
    }

    calcreate = calendarcreator.CalendarCreator()

    calcreate.set_margin(margin)
    calcreate.show_margin(show_margin)
    calcreate.show_margin_line(show_margin_lines)
    calcreate.set_page_size(pagewidth, pageheight)
    calcreate.set_title(titlename, titlepic, titlepos, titleanchor)
    calcreate.set_shiftdict(shift_dict)
    calcreate.set_citations(get_citations(), citation_options)
    legend_options = {
        "font size":r"\footnotesize",
        "align":"right",
    }
    calcreate.set_legends(get_legends(pagewidth), legend_options)

    calcreate.footer_over_pic = True
    calcreate.theme = "light" # "dark"

    calcreate.texfolder = "texfiles"
    calcreate.calendar_filename = "calendar.pdf"

    calcreate.create_calendar(pics, year_start, month_start)
