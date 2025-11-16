import textwrap
import html

DEFAULT_TEXT_SIZE = 16

def translate_rules(rules: dict[str, str]) -> dict[str, str]:
    # prebake
    if "border" in rules:
        parts = rules["border"].split()
        if len(parts) >= 2:
            rules["border-color"] = parts[1]

    if "color" in rules:
        assert "fill" not in rules, "panic"
        rules["fill"] = rules["color"]
        del rules["color"]
    if "border-color" in rules:
        assert "border-color" not in rules, "panic"
        rules["stroke"] = rules["border-color"]
        del rules["border-color"]

    # TODO: font

    return rules

def vectorize_text(text: str, style: dict[str, str], id: str = ""):
    style_element = ""
    if style:
        rules = "\n".join([f"{rn}: {rv}" for rn, rv in translate_rules(style).items()])
        style_element = textwrap.dedent(f'''
        <style>
            text {{
                {rules}
            }}
        </style>
        ''')

    svg_element = textwrap.dedent(f'''
    <svg>{textwrap.indent(style_element, "    " * 2)}
        <text y="{DEFAULT_TEXT_SIZE}">{html.escape(text)}</text>
    </svg>''').strip("\n")

    print(svg_element)

def vectorize_header(text: str, level: int):
    sizes = {
        1: "2em",
        2: "1.5em",
        3: "1.17em",
        4: "1em",
        5: ".83em",
        6: ".67em",
    }

if __name__ == "__main__":
    vectorize_text("hello", {"yes": "no"})
