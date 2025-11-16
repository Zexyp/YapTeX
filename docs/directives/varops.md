?DECLARE_DIRECTIVE(`#set <VARIABLE> {"<value>",<number>}`)

Sets a custom variable
```md
\#set NUMERIC_VAR 0
\#set NUMERIC_VAR=0
\#set NUMERIC_VAR = 0

\#set TEXT_VAR "text"
\#set TEXT_VAR="text"
\#set TEXT_VAR = "text"
```

?DECLARE_END_DIRECTIVE

?DECLARE_DIRECTIVE(`#inc <VARIABLE> [by]`)

Increments a given variable by specified amount (default is 1).
```md
\#inc HELLO_VAR 1
```

?DECLARE_END_DIRECTIVE

?DECLARE_DIRECTIVE(`#dec <VARIABLE> [by]`)

Decrements a given variable by specified amount (default is 1).
```md
\#dec HELLO_VAR 1
```

?DECLARE_END_DIRECTIVE
