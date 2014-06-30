#!/usr/bin/env python
import cairo
import pango
import pangocairo

"""
TODO
- add something that allows you to make font a certain width
  (i.e. as large as possible s.t. it fits in given width)
  (sure this doesn't exist'?)
- figure out how to add images?
- figure out how to add symbols? (like eye for sentience, etc.)
- pretty great if can arrage cards on a page...
- make some of the bars into variables - like the left side of the colored boxes
  becomes STAT_BOX_EXTENT or something
- ALSO CONSIDER HORIZONTAL CARDS
  WITH LONG NAME ALONG TOP
  SMALL STATS ON SIDE OF BOTTOM HALF
  WITH FADED LINES 'EXTENDING' STATS OUT FOR EYE TO FOLLOW
  AND WIDE TEXT ON BOTTOM HALF
  Problem might be...cards less denseley packed, might waste space because
  description isn't long enough to take up whole line?'
"""

def p2u(x):
    # units_from_double might do this...
    return int(x*pango.SCALE)

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

def build_card(title, pwr, hp, ap, desc):
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
    font = pango.FontDescription(fontname + " 25")
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
    font = pango.FontDescription(fontname + " 10")
    layout.set_font_description(font)
    w = .76*WIDTH
    x,y = scale(0.0025, .5)
    write(ctx, pangocairo_ctx, layout, x,y, w, desc, pango.ALIGN_LEFT)
    
    with open("cairo_text.png", "wb") as image_file:
        surf.write_to_png(image_file)


if __name__=="__main__":
    build_card('chainsaw', 2,15,8, "stuff")
