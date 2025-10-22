?DECLARE_DIRECTIVE(`#define <NAME>[(<ARG>...)]` `#enddef`)

Using this directive you can create macros.
```md
\#define MACRO Hello World!
```

You can also pass in arguments to make it even more dynamic!
```md
\#define GREET(NAME; LASTNAME) Hello \%NAME \%LASTNAME!

\%GREET(Bingus; Dingus)
```

?DECLARE_END_DIRECTIVE
