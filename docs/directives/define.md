?DECLARE_DIRECTIVE(`#define <NAME>[(<ARG>...)]`)

Using this directive you can create macros.
```md
\#define MACRO Hello World!
```

To evaluate it use `?`.
```md
\?MACRO
```

You can also pass in arguments to make it even more dynamic!
```md
\#define GREET(NAME; LASTNAME) Hello \%NAME \%LASTNAME!

\?GREET(Bingus; Dingus)
```

For multiline ones escape the new line.
```md
\#define GIB_LIST \
- A\
- B\
- C

\?GIB_LIST
```

You can also remove defines.
```md
\#undef HELLO
```

?DECLARE_END_DIRECTIVE
