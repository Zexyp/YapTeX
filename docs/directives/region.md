?DECLARE_DIRECTIVE(`#region "<name>"`)

Creates a section. Sections are converted into headers with regard to depth.
You of course must end it.
```md
\#region "Hello"
Wolrd
\#endregion
```

If you want to dynamically select the current depth of a title you can use `-#`
```md
\-# Hello
```

?DECLARE_END_DIRECTIVE
