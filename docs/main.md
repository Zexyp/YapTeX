#include "utils.md"

#region "YapTeX"
**YapTeX** is a **Markdown** and *plain text* preprocessor. It's **the** very cool and simple overcomplicated solution.

#region "Features"
- Build targets
    - Markdown
    - HTML
    - PDF
- Cross-platform (**WallHoles** and **Penguins**!)
- Only pip dependencies
- Macros
- Customization
#endregion

#region "Documentation"
When using directives then the `#` symbol must be the first symbol of the line. If you want to start your line with a `#`, you will have to escape it by using a backslash (eg. `\#`).

#region "Basic Directives"
#include "directives/inclusion.md"
#include "directives/region.md"
#include "directives/define.md"
#include "directives/pagebreak.md"
#endregion

#region "Variable Directives"
#include "directives/varops.md"
#endregion

#region "Advanced Directives"
#include "directives/copy.md"
#include "directives/ifs.md"
#include "directives/messages.md"
#endregion

#region "Using Variables"
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
\%{HELLO:l} -> %{_HELLO:l}
\%{HELLO:u} -> %{_HELLO:u}
\%{HELLO:t} -> %{_HELLO:t}

\%{HELLO:bn} -> %{_HELLO:bn}
\%{HELLO:dn} -> %{_HELLO:dn}

\%{HELLO:html} -> %{_HELLO:html}
\%{HELLO:id}   -> %{_HELLO:id}
\%{HELLO:esc}  -> %{_HELLO:esc}
```

#region "Special Variables"
You can use some special predefined variables.
- `_YEAR_`: current year
- `_MONTH_`: current month of year
- `_DAY_`: current day of month
- `_HOUR_`: current hour of day (24 hour format)
- `_MINUTE_`: current minute of hour
- `_SECOND_`: current second of minute
- `__FILE__`: current file
- `__LINE__`: current line

#endregion
#endregion

#endregion

#endregion

*This document was build using YapTeX*
