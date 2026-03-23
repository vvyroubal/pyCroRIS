"""CLI sučelje za CroRIS CROSBI API klijent."""

import argparse
import json
import sys
from pathlib import Path

from crosbi.client import CrorisClient, set_client
from crosbi.config import Config
from crosbi.endpoints import financijeri, mozvag, osobe, projekti, ustanove
from crosbi.export.csv_export import to_csv
from crosbi.export.json_export import to_json


def cmd_projekt(args: argparse.Namespace) -> None:
    if args.id:
        p = projekti.get_projekt(args.id)
        print(json.dumps(p.to_dict(), ensure_ascii=False, indent=2))
    elif args.mbu:
        ps = projekti.get_projekti_po_ustanovi(args.mbu)
        _export(ps, args)
    else:
        ps = list(projekti.list_projekti())
        _export(ps, args)


def cmd_osoba(args: argparse.Namespace) -> None:
    if args.id:
        o = osobe.get_osoba(args.id)
    elif args.oib:
        o = osobe.get_osoba_by_oib(args.oib)
    elif args.projekt_id:
        result = osobe.get_osobe_projekta(args.projekt_id)
        _export(result, args)
        return
    else:
        print("Zadaj --id, --oib ili --projekt-id", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(o.to_dict(), ensure_ascii=False, indent=2))


def cmd_ustanova(args: argparse.Namespace) -> None:
    if args.id:
        u = ustanove.get_ustanova(args.id)
        print(json.dumps(u.to_dict(), ensure_ascii=False, indent=2))
    elif args.projekt_id:
        result = ustanove.get_ustanove_projekta(args.projekt_id)
        _export(result, args)
    else:
        print("Zadaj --id ili --projekt-id", file=sys.stderr)
        sys.exit(1)


def cmd_mozvag(args: argparse.Namespace) -> None:
    if args.cmd == "ustanove":
        result = mozvag.get_ustanove()
        _export(result, args)
    elif args.cmd == "financijeri":
        result = mozvag.get_financijere()
        _export(result, args)
    elif args.cmd == "projekti":
        if not args.ustanova_id or not args.godina:
            print("Zadaj --ustanova-id i --godina", file=sys.stderr)
            sys.exit(1)
        result = mozvag.get_projekti_ustanove(args.ustanova_id, args.godina)
        _export(result, args)
    elif args.cmd == "osoba":
        if args.mbz and args.godina:
            o = mozvag.get_osoba_po_mbz(args.mbz, args.godina)
        elif args.oib and args.ustanova_id and args.godina:
            o = mozvag.get_osoba_po_oib(args.ustanova_id, args.oib, args.godina)
        else:
            print("Zadaj (--mbz --godina) ili (--oib --ustanova-id --godina)", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(vars(o), ensure_ascii=False, indent=2))


def _export(items: list, args: argparse.Namespace) -> None:
    output = getattr(args, "output", None)
    fmt = getattr(args, "format", "json")
    if output:
        path = Path(output)
        if fmt == "csv":
            to_csv(items, path)
        else:
            to_json(items, path)
        print(f"Spremljeno u {path} ({len(items)} zapisa)")
    else:
        rows = [item.to_dict() if hasattr(item, "to_dict") else vars(item) for item in items]
        print(json.dumps(rows, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crosbi",
        description="CroRIS CROSBI Projekti API klijent",
    )
    parser.add_argument("--username", help="CroRIS korisničko ime (override .env)")
    parser.add_argument("--password", help="CroRIS lozinka (override .env)")
    parser.add_argument("--output", "-o", help="Izlazna datoteka (JSON ili CSV)")
    parser.add_argument(
        "--format", "-f", choices=["json", "csv"], default="json", help="Format ispisa"
    )

    sub = parser.add_subparsers(dest="resource", required=True)

    # --- projekt ---
    p_proj = sub.add_parser("projekt", help="Rad s projektima")
    p_proj.add_argument("--id", type=int, help="Interni ID projekta")
    p_proj.add_argument("--mbu", help="MBU kod ustanove")
    p_proj.set_defaults(func=cmd_projekt)

    # --- osoba ---
    p_osoba = sub.add_parser("osoba", help="Rad s osobama")
    p_osoba.add_argument("--id", type=int, help="Interni ID osobe")
    p_osoba.add_argument("--oib", help="OIB osobe")
    p_osoba.add_argument("--projekt-id", dest="projekt_id", type=int)
    p_osoba.set_defaults(func=cmd_osoba)

    # --- ustanova ---
    p_ust = sub.add_parser("ustanova", help="Rad s ustanovama")
    p_ust.add_argument("--id", type=int, help="Interni ID ustanove")
    p_ust.add_argument("--projekt-id", dest="projekt_id", type=int)
    p_ust.set_defaults(func=cmd_ustanova)

    # --- mozvag ---
    p_moz = sub.add_parser("mozvag", help="MOZVAG agregirani podaci")
    moz_sub = p_moz.add_subparsers(dest="cmd", required=True)

    moz_sub.add_parser("ustanove", help="Popis svih ustanova")
    moz_sub.add_parser("financijeri", help="Popis svih financijera")

    p_moz_proj = moz_sub.add_parser("projekti", help="Projekti ustanove za godinu")
    p_moz_proj.add_argument("--ustanova-id", dest="ustanova_id", type=int, required=True)
    p_moz_proj.add_argument("--godina", type=int, required=True)

    p_moz_osoba = moz_sub.add_parser("osoba", help="Sažetak projekata osobe")
    p_moz_osoba.add_argument("--mbz", help="Matični broj znanstvenika")
    p_moz_osoba.add_argument("--oib", help="OIB osobe")
    p_moz_osoba.add_argument("--ustanova-id", dest="ustanova_id", type=int)
    p_moz_osoba.add_argument("--godina", type=int, required=True)

    p_moz.set_defaults(func=cmd_mozvag)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.username or args.password:
        cfg = Config()
        if args.username:
            cfg.username = args.username
        if args.password:
            cfg.password = args.password
        set_client(CrorisClient(cfg))

    args.func(args)


if __name__ == "__main__":
    main()
