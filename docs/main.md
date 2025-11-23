#include "utils.md"

#region "YapTeX"
**YapTeX** is a **Markdown** and *plain text* preprocessor. It's **the** very *cool* and simply overcomplicated solution.

#region "Features"
- Build targets
    - Markdown
    - HTML
    - PDF
- Cross-platform (**WallHoles** and **Penguins**!)
- Only pip dependencies
- Macros
- Customization
#endregion

#region "Usage"
Usual markdown headers are not considered as directives.
When using directives the `#` symbol must be the first symbol of the line.
If you want to start your line with directive-like entry, you will have to escape the special char by using a backslash (e.g. `\#`).
Similarly, variables and macros can be escaped.

#region "Basic Directives"
#include "directives/inclusion.md"
#include "directives/region.md"
#include "directives/define.md"
#include "directives/pagebreak.md"
#endregion

#region "Variable Directives"
#include "directives/varops.md"
#endregion

#region "Advanced Directives"
#include "directives/copy.md"
#include "directives/ifs.md"
#include "directives/messages.md"
#endregion

#include "variables.md"

#endregion

#include "installation.md"

#endregion

-# Code Style
Notes based on pylint yap:
- If the *docstring* is not needed fill it with some yap (best is to use something thematic).
- "Too few public methods" indicates that the file or mechanism might be too clean. There is no point in making it more stupid.

---

> [!WARNING]
> Using YapTeX may result in:
> - High blood pressure
> - Existential crises
> - Endless nightmares
> - Complete failure of effort to document

*This document was built using YapTeX*
