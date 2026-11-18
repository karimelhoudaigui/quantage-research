"""C19-only Unicode typography and breakable inline code; historical renderer unchanged."""
import re
import build_paper as base

def code_tex(value):
    out=[];run=0
    for c in value:
        out.append(base.escape(c));run+=1
        if c in ',;:/[]()_+=-' or run>=10:
            out.append(r'\allowbreak{}');run=0
    return r'\texttt{'+''.join(out)+'}'

def inline(text):
    pattern=r'(\$[^$]+\$|`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*)'
    out=[]
    for token in re.split(pattern,text):
        if token.startswith('`') and token.endswith('`'):out.append(code_tex(token[1:-1]))
        else:out.append(ORIGINAL_INLINE(token))
    return ''.join(out)

ORIGINAL_PRE=base.pre
ORIGINAL_INLINE=base.inline

def pre(title):
    lines=ORIGINAL_PRE(title)
    lines=[x for x in lines if x not in (r'\usepackage[T1]{fontenc}',r'\usepackage[utf8]{inputenc}')]
    lines[1:1]=[r'\usepackage{fontspec}',r'\setmainfont{lmroman10-regular.otf}[BoldFont=lmroman10-bold.otf,ItalicFont=lmroman10-italic.otf,BoldItalicFont=lmroman10-bolditalic.otf]',r'\setmonofont{lmmono10-regular.otf}']
    index=lines.index(r'\newlength{\QAcolumnwidth}')
    lines[index:index]=[r'\emergencystretch=2em',r'\hypersetup{hidelinks}']
    return lines

def latex(markdown):
    # The build CLI is serial; restore globals immediately after conversion.
    previous_pre,previous_inline=base.pre,base.inline
    try:
        base.pre,base.inline=pre,inline
        return base.latex(markdown)
    finally:base.pre,base.inline=previous_pre,previous_inline
