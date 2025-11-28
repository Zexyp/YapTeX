-# CLI
-## Building a document
You can ivoke the installed module simply by running a command in terminal.
```sh
yaptex <input-file>
```

For more info use help flag:
```sh
yaptex -h
```

`rargs` are renderer arguments.
Each of them have identifier of the renderer they belong to as a prefix.
Value is speciefied after an equls sign and you can separate them with a semicolon like so: `id:arg1=value;id:arg2=other`

Example to tell html renderer to use *Roboto* as font family for body of the output document.
```sh
yaptex <input-file> --target html --rargs "html:font_family=Roboto"
```

> [!NOTE]
> HTML renderer is used as a middle step when targeting PDF.

-## Fonts
You can download more fonts from **Google Fonts** using the following command.
```sh
yaptex-font pull <font-family>
```

To see all installed fonts use:
```sh
yaptex-font list
```
