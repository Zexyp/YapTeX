
# YapTeX
**YapTeX** is a **Markdown** and *plain text* preprocessor. It's **the** very *cool* and simply overcomplicated solution.

## Features
- Build targets
    - Markdown
    - HTML
    - PDF
- Cross-platform (**WallHoles** and **Penguins**!)
- Only pip dependencies
- Macros
- Customization

## Usage


Usual markdown headers are not considered as directives.
When using directives the `#` symbol must be the first symbol of the line.
If you want to start your line with a `#`, you will have to escape it by using a backslash (e.g. `\#`).
Similarly, variables and macros can be escaped.

### Basic Directives
#### `#include "<filepath>"`


Includes another file.
```md
#include "some/other/file.md"
```


---


#### `#embed "<filepath>"`


Includes another file raw without processing it.
```md
#embed "some/other/file.txt"
```


---
#### `#region "<name>"`


Creates a section. Sections are converted into headers with regard to depth.
You of course must end it.
```md
#region "Hello"
Wolrd
#endregion
```

If you want to dynamically select the current depth of a title you can use `-#`
```md
-# Hello
```


---

#### `#define <NAME>[(<ARG>...)]`


Using this directive you can create macros.
```md
#define MACRO Hello World!
```

To evaluate it use `?`.
```md
?MACRO
```

You can also pass in arguments to make it even more dynamic!
```md
#define GREET(NAME; LASTNAME) Hello %NAME %LASTNAME!

?GREET(Bingus; Dingus)
```

For multiline ones escape the new line.
```md
#define GIB_LIST \
- A\
- B\
- C

?GIB_LIST
```

You can also remove defines.
```md
#undef HELLO
```


---

#### `#pagebreak`


Insert page breaking feature.
```md
#pagebreak
```


---


### Variable Directives
#### `#set <VARIABLE> {"<value>",<number>}`


Sets a custom variable
```md
#set NUMERIC_VAR 0
#set NUMERIC_VAR=0
#set NUMERIC_VAR = 0

#set TEXT_VAR "text"
#set TEXT_VAR="text"
#set TEXT_VAR = "text"
```


---


#### `#inc <VARIABLE> [by]`


Increments a given variable by specified amount (default is 1).
```md
#inc HELLO_VAR 1
```


---


#### `#dec <VARIABLE> [by]`


Decrements a given variable by specified amount (default is 1).
```md
#dec HELLO_VAR 1
```


---


### Advanced Directives
#### `#copy "<what>" "<where>"`


Copies a given file into directory that is relative to output directory. Mostly used for asset management.
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


#### `#ifdef <DEFINE>`


Includes content if defined and not empty (or not zero).
Needs end directive like other block directives.
```md
#ifdef HELLO
HELLO set
#elifdef BYE
BYE set
#else
I have no idea what's going on...
#endif
```

Also `#ifndef` and `#elifndef` can be used with inverted evaluation.
Some boolean operator can be used.
```md
#ifdef HELLO && BYE
What's going on
#endif

#ifndef HELLO || BYE
Nothing is defined :(
#endif
```


---
#### `#warning "<message>"`


Prints a message while building.
```md
#warning "We are doing number of cool things..."
```


---


#### `#error "<message>"`


Prints a message and stops the build.
```md
#error "Whoops..."
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
    - `slug`: slufify
    - `esc`: escape special characters (eg. `"`)


```md
%{HELLO:l} -> c:/users/fafa/je "cyp"?.txt
%{HELLO:u} -> C:/USERS/FAFA/JE "CYP"?.TXT
%{HELLO:t} -> C:/Users/Fafa/Je "Cyp"?.Txt

%{HELLO:bn} -> je "cYp"?.txt
%{HELLO:dn} -> C:/Users/faFa

%{HELLO:html} -> C:/Users/faFa/je &quot;cYp&quot;?.txt
%{HELLO:slug} -> cusersfafaje-cyptxt
%{HELLO:esc}  -> C:/Users/faFa/je \"cYp\"?.txt
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



## Installation
*TODO*


### Dependencies
#### xhtml2pdf

### Extension
You can build the [**Yapper**](yapper/README.md) extension VSIX file for **Visual Studio Code** using the default commands.
```sh
npm install
```
```sh
npx vsce package
```



*This document was built using YapTeX*
