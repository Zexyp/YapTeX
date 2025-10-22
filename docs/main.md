#include "utils.md"

#section "YapTeX"
**YapTeX** is a **Markdown** and *plain text* preprocessor. It's **the** very cool and simple overcomplicated solution.

#section "Features"
- Build targets
    - Markdown
    - HTML
    - PDF
- Cross-platform (**WallHoles** and **Penguins**!)
- Only pip dependencies
- Macros
- Customization
#endsect

#section "Documentation"
When using directives then the `#` symbol must be the first symbol of the line. If you want to start your line with a `#`, you will have to escape it by using a backslash (eg. `\#`).

#section "Basic Directives"
#include "directives/include.md"
#include "directives/section.md"
#include "directives/define.md"
#include "directives/pagebreak.md"
#endsect

#section "Variable Directives"
#include "directives/set.md"
#include "directives/increment.md"
#endsect

#section "Advanced Directives"
#include "directives/copy.md"
#include "directives/if.md"
#include "directives/warning.md"
#endsect

#section "Using Variables"
Varibles can be placed anywhere using the `%` symbol as a prefix.
```md
\%HELLO
```

There are multiple variable formatting options while pasting. You can access them by prefixing the prefix symbol.
- Basic
    - `l`: convert to lower case
    - `u`: convert to upper case
    - `t`: convert to title case
- Files
    - `bn`: filepath basename
    - `dn`: filepath dirname
- Special
    - `html`: html escape given value
    - `id`: convert to id
    - `esc`: escape special characters (eg. `"`)

#set _HELLO "C:/Users/faFa/je \"cYp\"?.txt"

```
\%{HELLO:l} -> \%{_HELLO:l}
\%{HELLO:u} -> \%{_HELLO:u}
\%{HELLO:t} -> \%{_HELLO:t}

\%{HELLO:bn} -> \%{_HELLO:bn}
\%{HELLO:dn} -> \%{_HELLO:dn}

\%{HELLO:html} -> \%{_HELLO:html}
\%{HELLO:id}   -> \%{_HELLO:id}
\%{HELLO:esc}  -> \%{_HELLO:esc}
```

#section "Special Variables"
You can use some special predefined variables.
- `_YEAR_`: current year
- `_MONTH_`: current month of year
- `_DAY_`: current day of month
- `_HOUR_`: current hour of day (24 hour format)
- `_MINUTE_`: current minute of hour
- `_SECOND_`: current second of minute
- `__FILE__`: current file
- `__LINE__`: current line

#endsect
#endsect

#endsect

#endsect

*This document was build using YapTeX*

#### TODO
- Consider different string quoting
- Build targets