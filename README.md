


# YapTeX
**YapTeX** is a **Markdown** and *plain text* preprocessor. It's **the** very cool and simple overcomplicated solution.

## Features
- Build targets
    - Markdown
    - HTML
    - PDF
- Cross-platform (**WallHoles** and **Penguins**!)
- Only pip dependencies
- Macros
- Customization

## Documentation
When using directives then the `#` symbol must be the first symbol of the line. If you want to start your line with a `#`, you will have to escape it by using a backslash (eg. `\#`).

### Basic Directives
#### `#include "<filepath>"`

Includes another file.
```md
#include "some/other/file.md"
```

---

#### `#section "<name>"` `#endsect`

Creates a section. Sections are converted into headers with regard to depth.
```md
#section "Hello"
Wolrd
#endsect
```

---

#### `#define <NAME>[(<ARG>...)]` `#enddef`

Using this directive you can create macros.
```md
#define MACRO
Hello World!
#enddef
```

You can also pass in arguments to make it even more dynamic!
```md
#define GREET(NAME; LASTNAME)
Hello %NAME %LASTNAME!
#enddef

#GREET(Bingus; Dingus)
```

---

#### `#pagebreak`

Insert page braking feature.
```md
#pagebreak
```

---


### Variable Directives
#### `#set <VARIABLE> {"<value>",<number>}`

Sets a custom variable
```md
#set HELLO_VAR1 "text"
#set HELLO_VAR2 0
```

---

#### `#increment <VARIABLE> <by>`

Increments a given variable by specified amount.
```md
#increment HELLO_VAR 1
```

---


### Advanced Directives
#### `#copy "<what>" "<where>"`

Copies a gived file to directory relative to the output directory. Mostly used for asset management.
```md
#copy "images/memisek.jpg" "assets"
```

---

#### `#if "<VARIABLE>"` `#elif "<VARIABLE>"` `#else` `#endif`

Includes content if variable is defined and isn't empty (or not zero). Also needs to be ended like other block directives.
```md
#if HELLO
HELLO set
#elif BYE
BYE set
#else
I have no idea what's going on...
#endif
```

---

#### `#warning "<message>"`

Prints a message while building.
```md
#warning "We are doing number of cool things..."
```

---


### Using Variables
Varibles can be placed anywhere using the `%` symbol as a prefix.
```md
%HELLO
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


```
l%HELLO -> c:/users/fafa/je "cyp"?.txt
u%HELLO -> C:/USERS/FAFA/JE "CYP"?.TXT
t%HELLO -> C:/Users/Fafa/Je "Cyp"?.Txt

bn%HELLO -> je "cYp"?.txt
dn%HELLO -> C:/Users/faFa

html%HELLO -> C:/Users/faFa/je &quot;cYp&quot;?.txt
id%HELLO   -> cusersfafaje-cyptxt
esc%HELLO  -> C:/Users/faFa/je \"cYp\"?.txt
```

#### Special Variables
You can use some special predefined variables.
- `_YEAR_`: current year
- `_MONTH_`: current month of year
- `_DAY_`: current day of month
- `_HOUR_`: current hour of day (24 hour format)
- `_MINUTE_`: current minute of hour
- `_SECOND_`: current second of minute
- `__FILE__`: current file
- `__LINE__`: current line




*This document was build using YapTeX*

#### TODO
- Consider different string quoting
- Build targets