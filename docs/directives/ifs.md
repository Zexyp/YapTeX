?DECLARE_DIRECTIVE(`#if <VARIABLE>)
Includes content if variable is defined and isn't empty (or not zero). Also needs to be ended like other block directives.
```md
\#if HELLO
HELLO set
\#elif BYE
BYE set
\#else
I have no idea what's going on...
\#endif
```

?DECLARE_END_DIRECTIVE

?DECLARE_DIRECTIVE(`#ifdef <DEFINE>`)

Includes content if defined and not empty (or not zero).
Needs end directive like other block directives.
```md
\#ifdef HELLO
HELLO set
\#elifdef BYE
BYE set
\#else
I have no idea what's going on...
\#endif
```

Also `#ifndef` and `#elifndef` can be used with inverted evaluation.
Some boolean operator can be used.
```md
\#ifdef HELLO && BYE
What's going on
\#endif

\#ifndef HELLO || BYE
Nothing is defined :(
\#endif
```

?DECLARE_END_DIRECTIVE
