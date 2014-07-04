#!/usr/bin/env python
import cairo
import pango
import pangocairo
import csv

"""
TODO
- need to make read in CSV files now
- add something that allows you to make font a certain width
  (i.e. as large as possible s.t. it fits in given width)
  (sure this doesn't exist'?)
- figure out how to add images?
- figure out how to add symbols? (like eye for sentience, etc.)
- make some of the bars into variables - like the left side of the colored boxes
  becomes STAT_BOX_EXTENT or something
- ALSO CONSIDER HORIZONTAL CARDS
  WITH LONG NAME ALONG TOP
  SMALL STATS ON SIDE OF BOTTOM HALF
  WITH FADED LINES 'EXTENDING' STATS OUT FOR EYE TO FOLLOW
  AND WIDE TEXT ON BOTTOM HALF
  Problem might be...cards less denseley packed, might waste space because
  description isn't long enough to take up whole line?'
- make fonts and line thicknesses scale with card?
  naww, just resize the card if you need to...it's a vector graphic!
"""

def p2u(x):
    # units_from_double might do this...
    return int(x*pango.SCALE)

def csv_to_cards(filename):
    # open csv file and return list of cards for passing to build_pages
    cards = []
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            #print '\n'.join(row)
            name, pos, hp, pwr, ap, desc = row 
            cards.append((name, hp, pwr, ap, desc))
    return cards
    
def write(ctx, pctx, layout, x, y, width, text, alignment, center_vert=None):
    # to center vertically, make sure 'y' is the line you want to center on
    ctx.move_to(x,y)
    layout.set_text(text)
    layout.set_alignment(alignment)
    if width:
        # wrapping stuff
        layout.set_wrap(pango.WRAP_WORD)
        layout.set_width(p2u(width))
        layout.set_spacing(p2u(-3))
    if center_vert:
        # assume want to center vertically...
        w,h = layout.get_pixel_size()
        ctx.move_to(x,y-h/2.)
    pctx.update_layout(layout)
    pctx.show_layout(layout)

def build_card(title, hp,pwr,ap, desc, save=False):
    WIDTH, HEIGHT = 350, 500
    scale = lambda x, y: (x*WIDTH, y*HEIGHT)
    
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surf)
    #ctx.scale(WIDTH, HEIGHT) # Normalizing the canvas

    #draw a background rectangle:
    ctx.rectangle(0,0, WIDTH, HEIGHT)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()

    # draw colored attribute boxes
    sx,sy = scale(.75, .5)
    ex,ey = scale(1, .5+.5/3)
    ctx.rectangle(sx,sy, ex,ey)
    ctx.set_source_rgba(0, .6, 0, 1)#0.60)
    ctx.fill()

    sx,sy = scale(0.75, .5+.5/3)
    ex,ey = scale(1, .5/3)
    ctx.rectangle(sx,sy, ex,ey)
    ctx.set_source_rgba(.6, 0, 0, 1)#0.40)
    ctx.fill()

    sx,sy = scale(0.75, .5+2*.5/3)
    ex,ey = scale(1, .5/3)
    ctx.rectangle(sx,sy, ex,ey)
    ctx.set_source_rgba(0, 0, .6, 1)#0.40)
    ctx.fill()

    # make lines black and thick
    ctx.set_line_width(3)
    ctx.set_source_rgb(0, 0, 0)

    # draw a line splitting the top and bottom halves
    ctx.move_to(*scale(0,.5))
    ctx.line_to(*scale(1,.5))
    ctx.stroke()  
    
    # draw lines separating the boxes
    ctx.move_to(*scale(.75,.5+.5/3))
    ctx.line_to(*scale(1,.5+.5/3))
    ctx.stroke()    

    ctx.move_to(*scale(.75,.5+2*.5/3))
    ctx.line_to(*scale(1,.5+2*.5/3))
    ctx.stroke()    

    # draw lighter lines 'extending' stat boxes
    ctx.set_source_rgb(.95,.95,.95)
    ctx.move_to(*scale(0,.5+.5/3))
    ctx.line_to(*scale(.75,.5+.5/3))
    ctx.stroke()    

    ctx.move_to(*scale(0,.5+2*.5/3))
    ctx.line_to(*scale(.75,.5+2*.5/3))
    ctx.stroke()

    # draw left line of stat boxes
    ctx.set_source_rgb(0,0,0)
    ctx.move_to(*scale(.75,.5))
    ctx.line_to(*scale(.75,1))
    ctx.stroke()
    
    # init pango stuff
    pangocairo_ctx = pangocairo.CairoContext(ctx)
    pangocairo_ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
    ctx.set_source_rgb(0, 0, 0)
    layout = pangocairo_ctx.create_layout()
    fontname = "Ubuntu Mono"

    # write name
    font = pango.FontDescription(fontname + " 40")
    layout.set_font_description(font)
    w = WIDTH
    x,y = scale(0, .25)
    write(ctx, pangocairo_ctx, layout, x,y, w, title, pango.ALIGN_CENTER, True)

    # write stats
    ctx.set_source_rgb(1,1,1)
    font = pango.FontDescription(fontname + " 15")
    layout.set_font_description(font)
    w = 0.25*WIDTH
    x,y = scale(.75, .5+1./12)
    write(ctx, pangocairo_ctx, layout, x,y,w, str(hp), pango.ALIGN_CENTER, True)
    x,y = scale(.75, .5+3./12)
    write(ctx, pangocairo_ctx, layout, x,y,w, str(pwr),pango.ALIGN_CENTER, True)
    x,y = scale(.75, .5+5./12)
    write(ctx, pangocairo_ctx, layout, x,y,w, str(ap), pango.ALIGN_CENTER, True)

    # write description
    ctx.set_source_rgb(0, 0, 0)
    font = pango.FontDescription(fontname + " 12")
    layout.set_font_description(font)
    w = .76*WIDTH
    x,y = scale(0.0025, .5)
    write(ctx, pangocairo_ctx, layout, x,y, w, desc, pango.ALIGN_LEFT)
    #x,y = scale(0.0025, .75)
    #write(ctx, pangocairo_ctx, layout, x,y, w, desc, pango.ALIGN_LEFT, True)


    # save to PNG if want to
    if save:
        surf.write_to_png("test_card.png")

    return surf

def build_pages(cards_w, cards_h, cards):
    # passes the proper amount of cards to build_page, saves each page
    num_cards = cards_w * cards_h
    i = 0
    while cards:
        build_page(cards_w, cards_h, cards, "page"+str(i))
        cards = cards[num_cards:]
        i += 1
    pass
    
def build_page(cards_w, cards_h, cards, filename="test_page"):
    # cards_h and cards_v are number of cards wide and high
    # cards is a list of (title, pwr, hp, ap, desc) tuples
    # border to surround each card, in pixels
    BORDER = 5
    # convert cards to a list of surfaces
    card_surfs = [build_card(*args) for args in cards]
    # TODO: assume they all have the same length - should check!
    cw, ch = card_surfs[0].get_width(), card_surfs[0].get_height()
    WIDTH  = cards_w*cw + BORDER*(cards_w+1)
    HEIGHT = cards_h*ch + BORDER*(cards_h+1)

    # make surface
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surf)
    ctx.rectangle(0,0, WIDTH, HEIGHT)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    
    # fill with cards
    cx, cy = BORDER, BORDER #0, 0
    for cs in card_surfs:
        # draw card
        ctx.set_source_surface(cs, cx, cy)
        ctx.paint()
        # update drawing position
        cx += cw + BORDER  
        if cx >= WIDTH:
            cx = BORDER
            cy += ch + BORDER

    # save
    surf.write_to_png(filename+".png")

    
if __name__=="__main__":
    text = "Melee: +1 POW when used near target\n\nEdged"
    name = 'chainsaw'
    hp = "8/12/+0"
    pwr = "4"
    ap = "-3/0/+0"
    card = (name, hp,pwr,ap, text, True)
    #build_card(*card)
    #build_page(3,5, [card for _ in range(10)])
    #build_pages(2,2, [card for _ in range(10)])
    cards = csv_to_cards('cards.csv')
    build_pages(2, 2, cards)
