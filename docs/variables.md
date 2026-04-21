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
    - `slug`: slufify
    - `esc`: escape special characters (eg. `"`)

#set HELLO "C:/Users/faFa/je \"cYp\"?.txt"

```md
\%{HELLO:l} -> %{HELLO:l}
\%{HELLO:u} -> %{HELLO:u}
\%{HELLO:t} -> %{HELLO:t}

\%{HELLO:bn} -> %{HELLO:bn}
\%{HELLO:dn} -> %{HELLO:dn}

\%{HELLO:html} -> %{HELLO:html}
\%{HELLO:slug} -> %{HELLO:slug}
\%{HELLO:esc}  -> %{HELLO:esc}
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
