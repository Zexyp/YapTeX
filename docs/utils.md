#define DECLARE_DIRECTIVE(NAME)
#section "esc%NAME"
#enddef

#define DECLARE_END_DIRECTIVE
#endsect
---
#enddef

#define PLACE_DECLARED
<ul>
%LIST_DIRECTIVES
<ul>
#enddef
