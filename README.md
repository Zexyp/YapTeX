## Examples

```md
#include "some/other/file.md"
```

```md
#copy "some/image.png" "assets/img.png"
```

```md
#section "Hello"
Wolrd
#endsection
```

```md
#define SIMPLE
This one is shrimple
#enddefine

#define MACRO(X; Y)
Macro parametrs X: %X and Y: %Y
#enddefine

#SIMPLE
#MACRO(a; b)
```
