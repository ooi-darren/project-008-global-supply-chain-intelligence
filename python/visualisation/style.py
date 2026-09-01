# House chart style v2: consulting-exhibit conventions (MBB-style).
# Gray for context series, one or two accent colors for what the title is
# actually about, direct end-of-line/bar labels instead of a legend box.
import matplotlib.pyplot as plt
import textwrap

ACCENT_1 = '#2a78d6'   # primary accent, the series the title is about
ACCENT_2 = '#eb6834'   # secondary accent, used only for genuine two-way comparisons
                        # or a title that names two co-equal findings
GRAY = '#9a9a95'        # de-emphasized / context series, same family, faded out
INK, INK_SECONDARY, INK_MUTED = '#0b0b0b', '#52514e', '#898781'
GRID, SURFACE = '#ececea', '#fcfcfb'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'text.color': INK,
    'axes.edgecolor': '#c3c2b7',
    'axes.labelcolor': INK_SECONDARY,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'axes.axisbelow': True,
    'axes.grid.axis': 'y',
    'grid.color': GRID,
    'grid.linewidth': 0.7,
    'xtick.color': INK_MUTED,
    'ytick.color': INK_MUTED,
    'figure.facecolor': SURFACE,
    'axes.facecolor': SURFACE,
    'savefig.facecolor': SURFACE,
    'legend.frameon': False,
})

def add_source(fig, text, fontsize=8.5, color=None):
    """Small muted source/classification footnote, consulting-deck style.

    fig.text() draws one unwrapped line with no width limit of its own, so a
    long footnote silently forces savefig(bbox_inches='tight') to widen the
    whole canvas around it -- the image balloons sideways with a matching
    dead-space gap next to the actual chart. Measure the text's actual
    rendered width and only wrap (to a width derived from that real
    measurement) when it would overflow; a footnote that already fits is
    left untouched, so this can't reflow every other chart's footnote.
    """
    txt = fig.text(0.01, -0.04, text, ha='left', va='top', fontsize=fontsize,
                    color=color or INK_MUTED, style='italic', transform=fig.transFigure)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox_in = txt.get_window_extent(renderer).transformed(fig.dpi_scale_trans.inverted())
    max_width_in = fig.get_size_inches()[0] - 0.05
    if bbox_in.width > max_width_in:
        chars_per_line = max(40, int(len(text) * max_width_in / bbox_in.width))
        txt.set_text(textwrap.fill(text, width=chars_per_line))
    return txt

def end_label(ax, x, y, text, color, weight='semibold', va='center', offset=8):
    """Direct label at a line's endpoint, replacing a legend box."""
    ax.annotate(text, xy=(x, y), xytext=(offset, 0), textcoords='offset points',
                 va=va, ha='left', fontsize=10.5, fontweight=weight, color=color)
