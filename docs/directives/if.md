#DECLARE_DIRECTIVE(`#if "<VARIABLE>"` `#elif "<VARIABLE>"` `#else` `#endif`)

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

#DECLARE_END_DIRECTIVE
