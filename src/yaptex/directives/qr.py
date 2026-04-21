import argparse
import io
import base64
import decimal

import qrcode

from . import ArgDirective

# https://qr-platba.cz/wp-content/uploads/1645-standard-qr-v1-2-cerven-2021.pdf
class QrDirective(ArgDirective):
    trigger_on = ["qr"]

    class AccountAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if not hasattr(namespace, "account"):
                parser.error(f"{option_string} is only allowed when --account is specified")
            setattr(namespace, self.dest, values)

    def _create_payment_qr_data(self, args: argparse.Namespace):
        def parser_assert(condition, msg):
            if not condition:
                self.parser.error(msg)

        account = args.account.strip().replace(" ", "") # cleanup
        assert len(account) <= 46, "too long"
        
        data = f"SPD*1.0*ACC:{account.upper()}"

        if args.amount:
            decimal_places = -args.amount.as_tuple().exponent
            parser_assert(decimal_places <= 2, "amount: too many decimal places")
            parser_assert(len(str(args.amount)) <= 10, "amount: too long")
            data += f"*AM:{args.amount}"
        if args.currency:
            parser_assert(len(args.currency) == 3, "currency: unexpected code length")
            data += f"*CC:{args.currency.upper()}"
        if args.message:
            parser_assert(len(args.message) <= 60, "message: too long")
            data += f"*MSG:{args.message.upper()}"
        if args.x_variable:
            parser_assert(len(args.x_variable) <= 10, "x_variable: too long")
            data += f"*X-VS:{args.x_variable.upper()}"
        if args.x_specific:
            parser_assert(len(args.x_specific) <= 10, "x_specific: too long")
            data += f"*X-SS:{args.x_specific.upper()}"
        if args.x_constant:
            parser_assert(len(args.x_constant) <= 10, "x_constant: too long")
            data += f"*X-KS:{args.x_constant.upper()}"

        return data

    def build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser("qr", add_help=False, usage=argparse.SUPPRESS)
        parser.add_argument("data", metavar="<data>", nargs="?")
        parser.add_argument("--alt", required=False)
        parser.add_argument("--width", "-w", metavar="VALUE[UNIT]", required=False)
        parser.add_argument("--height", "-h", metavar="VALUE[UNIT]", required=False)

        parser.add_argument("--account", metavar="IBAN[+BIC]", required=False)
        parser.add_argument("--amount", action=self.AccountAction, type=decimal.Decimal, required=False)
        # TODO: fuck ALT-ACC rn
        # FIXME: currency is retarded
        parser.add_argument("--currency", metavar="CODE", action=self.AccountAction, choices=_known_currencies, required=False)
        # TODO: fuck DT rn
        parser.add_argument("--message", metavar="MSG", action=self.AccountAction, required=False)
        parser.add_argument("--x-variable", metavar="SYMBOL", action=self.AccountAction, required=False)
        parser.add_argument("--x-specific", metavar="SYMBOL", action=self.AccountAction, required=False)
        parser.add_argument("--x-constant", metavar="SYMBOL", action=self.AccountAction, required=False)

        def func(args):
            if (args.data is None) == (args.account is None):
                parser.error("provide either <data> or --account")
            
            data = args.data
            if args.account:
                data = self._create_payment_qr_data(args)

            # load with data
            qr = qrcode.QRCode()
            qr.add_data(data)
            qr.make()

            # create
            img = qr.make_image(fill_color="black", back_color="white")

            # save to buffer
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            b64data = base64.b64encode(buffer.read()).decode("utf-8")

            # craft attribs
            attributes = []
            attributes.append(f"src=\"data:image/png;base64,{b64data}\"")
            if args.alt:
                attributes.append(f"alt=\"{args.alt}\"")
            style = []
            if args.width:
                if args.width.isdecimal():
                    attributes.append(f"width=\"{args.width}\"")
                else:
                    style.append(f"width: {args.width}")
            if args.height:
                if args.height.isdecimal():
                    attributes.append(f"height=\"{args.height}\"")
                else:
                    style.append(f"height: {args.height}")
            if style:
                attributes.append(f"style=\"{"; ".join(style)}\"")
                
            return f"<img {" ".join(attributes)}/>"

        parser.set_defaults(func=func)
        return parser

# https://en.wikipedia.org/wiki/ISO_4217#Active_codes_(list_one)
# ISO 4217 active
_known_currencies = [
    "AED",
    "AFN",
    "ALL",
    "AMD",
    "AOA",
    "ARS",
    "AUD",
    "AWG",
    "AZN",
    "BAM",
    "BBD",
    "BDT",
    "BHD",
    "BIF",
    "BMD",
    "BND",
    "BOB",
    "BOV",
    "BRL",
    "BSD",
    "BTN",
    "BWP",
    "BYN",
    "BZD",
    "CAD",
    "CDF",
    "CHE",
    "CHF",
    "CHW",
    "CLF",
    "CLP",
    "CNY",
    "COP",
    "COU",
    "CRC",
    "CUP",
    "CVE",
    "CZK",
    "DJF",
    "DKK",
    "DOP",
    "DZD",
    "EGP",
    "ERN",
    "ETB",
    "EUR",
    "FJD",
    "FKP",
    "GBP",
    "GEL",
    "GHS",
    "GIP",
    "GMD",
    "GNF",
    "GTQ",
    "GYD",
    "HKD",
    "HNL",
    "HTG",
    "HUF",
    "IDR",
    "ILS",
    "INR",
    "IQD",
    "IRR",
    "ISK",
    "JMD",
    "JOD",
    "JPY",
    "KES",
    "KGS",
    "KHR",
    "KMF",
    "KPW",
    "KRW",
    "KWD",
    "KYD",
    "KZT",
    "LAK",
    "LBP",
    "LKR",
    "LRD",
    "LSL",
    "LYD",
    "MAD",
    "MDL",
    "MGA",
    "MKD",
    "MMK",
    "MNT",
    "MOP",
    "MRU",
    "MUR",
    "MVR",
    "MWK",
    "MXN",
    "MXV",
    "MYR",
    "MZN",
    "NAD",
    "NGN",
    "NIO",
    "NOK",
    "NPR",
    "NZD",
    "OMR",
    "PAB",
    "PEN",
    "PGK",
    "PHP",
    "PKR",
    "PLN",
    "PYG",
    "QAR",
    "RON",
    "RSD",
    "RUB",
    "RWF",
    "SAR",
    "SBD",
    "SCR",
    "SDG",
    "SEK",
    "SGD",
    "SHP",
    "SLE",
    "SOS",
    "SRD",
    "SSP",
    "STN",
    "SVC",
    "SYP",
    "SZL",
    "THB",
    "TJS",
    "TMT",
    "TND",
    "TOP",
    "TRY",
    "TTD",
    "TWD",
    "TZS",
    "UAH",
    "UGX",
    "USD",
    "USN",
    "UYI",
    "UYU",
    "UYW",
    "UZS",
    "VED",
    "VES",
    "VND",
    "VUV",
    "WST",
    "XAD",
    "XAF",
    "XAG",
    "XAU",
    "XBA",
    "XBB",
    "XBC",
    "XBD",
    "XCD",
    "XCG",
    "XDR",
    "XOF",
    "XPD",
    "XPF",
    "XPT",
    "XSU",
    "XTS",
    "XUA",
    "XXX",
    "YER",
    "ZAR",
    "ZMW",
    "ZWG",
]