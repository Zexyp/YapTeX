?DECLARE_DIRECTIVE(`#set <VARIABLE> {"<value>",<number>}`)

Sets a custom variable
```md
\#set HELLO_VAR1 "text"
\#set HELLO_VAR2 0
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
