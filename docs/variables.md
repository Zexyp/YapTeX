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

#set _HELLO "C:/Users/faFa/je \"cYp\"?.txt"

```md
\%{HELLO:l} -> %{_HELLO:l}
\%{HELLO:u} -> %{_HELLO:u}
\%{HELLO:t} -> %{_HELLO:t}

\%{HELLO:bn} -> %{_HELLO:bn}
\%{HELLO:dn} -> %{_HELLO:dn}

\%{HELLO:html} -> %{_HELLO:html}
\%{HELLO:slug} -> %{_HELLO:slug}
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