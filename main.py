"""CLI sučelje za CroRIS API klijent (svi moduli)."""

import argparse
import json
import sys
from pathlib import Path

from crosbi.client import CrorisClient, set_client
from crosbi.config import Config
from crosbi.endpoints import (
    casopisi,
    dogadanja,
    financijeri,
    mozvag,
    oprema_api,
    osobe,
    projekti,
    publikacije_crosbi,
    ustanove,
    upisnik,
    znanstvenici,
)
from crosbi.export.csv_export import to_csv
from crosbi.export.json_export import to_json


# ---------------------------------------------------------------------------
# Pomoćne funkcije
# ---------------------------------------------------------------------------


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


def _print_one(obj) -> None:
    data = obj.to_dict() if hasattr(obj, "to_dict") else vars(obj)
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Handleri
# ---------------------------------------------------------------------------


def cmd_projekt(args: argparse.Namespace) -> None:
    if args.id:
        _print_one(projekti.get_projekt(args.id))
    elif args.mbu:
        _export(projekti.get_projekti_po_ustanovi(args.mbu), args)
    else:
        _export(list(projekti.list_projekti()), args)


def cmd_osoba(args: argparse.Namespace) -> None:
    if args.id:
        _print_one(osobe.get_osoba(args.id))
    elif args.oib:
        _print_one(osobe.get_osoba_by_oib(args.oib))
    elif args.projekt_id:
        _export(osobe.get_osobe_projekta(args.projekt_id), args)
    else:
        print("Zadaj --id, --oib ili --projekt-id", file=sys.stderr)
        sys.exit(1)


def cmd_ustanova(args: argparse.Namespace) -> None:
    if args.id:
        _print_one(ustanove.get_ustanova(args.id))
    elif args.projekt_id:
        _export(ustanove.get_ustanove_projekta(args.projekt_id), args)
    else:
        print("Zadaj --id ili --projekt-id", file=sys.stderr)
        sys.exit(1)


def cmd_mozvag(args: argparse.Namespace) -> None:
    if args.cmd == "ustanove":
        _export(mozvag.get_ustanove(), args)
    elif args.cmd == "financijeri":
        _export(mozvag.get_financijere(), args)
    elif args.cmd == "projekti":
        if not (args.ustanova_id and args.godina):
            print("Zadaj --ustanova-id i --godina", file=sys.stderr)
            sys.exit(1)
        _export(mozvag.get_projekti_ustanove(args.ustanova_id, args.godina), args)
    elif args.cmd == "osoba":
        if args.mbz and args.godina:
            _print_one(mozvag.get_osoba_po_mbz(args.mbz, args.godina))
        elif args.oib and args.ustanova_id and args.godina:
            _print_one(mozvag.get_osoba_po_oib(args.ustanova_id, args.oib, args.godina))
        else:
            print("Zadaj (--mbz --godina) ili (--oib --ustanova-id --godina)", file=sys.stderr)
            sys.exit(1)


def cmd_upisnik(args: argparse.Namespace) -> None:
    if args.cmd == "sve":
        _export(upisnik.get_sve_aktivne_ustanove(), args)
    elif args.cmd == "znanstvene":
        _export(upisnik.get_znanstvene_ustanove(), args)
    elif args.cmd == "visoka-ucilista":
        _export(upisnik.get_visoka_ucilista(), args)
    elif args.cmd == "jzi":
        _export(upisnik.get_javni_znanstveni_instituti(), args)
    elif args.cmd == "neaktivne":
        _export(upisnik.get_neaktivne_ustanove(), args)
    elif args.cmd == "id":
        _print_one(upisnik.get_ustanova_by_id(args.ustanova_id))
    elif args.cmd == "mbu":
        _print_one(upisnik.get_ustanova_by_mbu(args.mbu_kod))
    elif args.cmd == "ppg":
        _export(upisnik.get_sva_podrucja(), args)


def cmd_crosbi(args: argparse.Namespace) -> None:
    if args.id:
        _print_one(publikacije_crosbi.get_publikacija(args.id))
    elif args.osoba_id:
        _print_one(publikacije_crosbi.get_publikacije_osobe(args.osoba_id))
    elif args.mbz:
        _print_one(publikacije_crosbi.get_publikacije_osobe_by_mbz(args.mbz))
    elif args.projekt_id:
        _print_one(publikacije_crosbi.get_publikacije_projekta(args.projekt_id))
    elif args.ustanova_id:
        _print_one(publikacije_crosbi.get_publikacije_ustanove(args.ustanova_id))
    else:
        print("Zadaj --id, --osoba-id, --mbz, --projekt-id ili --ustanova-id", file=sys.stderr)
        sys.exit(1)


def cmd_oprema(args: argparse.Namespace) -> None:
    if args.id:
        _print_one(oprema_api.get_oprema(args.id))
    elif args.usluga_id:
        _print_one(oprema_api.get_usluga(args.usluga_id))
    elif args.list_usluge:
        _export(list(oprema_api.list_usluge()), args)
    else:
        _export(list(oprema_api.list_oprema()), args)


def cmd_casopisi(args: argparse.Namespace) -> None:
    if args.id:
        _print_one(casopisi.get_casopis(args.id))
    else:
        _export(list(casopisi.list_casopisi()), args)


def cmd_dogadanja(args: argparse.Namespace) -> None:
    if args.id:
        _print_one(dogadanja.get_dogadanje(args.id))
    else:
        _export(list(dogadanja.list_dogadanja()), args)


def cmd_znanstvenici(args: argparse.Namespace) -> None:
    if args.oib:
        _print_one(znanstvenici.get_znanstvenik_by_oib(args.oib))
    elif args.mbz:
        _print_one(znanstvenici.get_znanstvenik_by_mbz(args.mbz))
    elif args.akreditacije_org_id:
        _export(znanstvenici.get_akreditacije_ustanove(args.akreditacije_org_id), args)
    else:
        _export(list(znanstvenici.list_znanstvenici()), args)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crosbi",
        description="CroRIS API klijent — svi moduli",
    )
    parser.add_argument("--username", help="CroRIS korisničko ime (override .env)")
    parser.add_argument("--password", help="CroRIS lozinka (override .env)")
    parser.add_argument("--output", "-o", help="Izlazna datoteka")
    parser.add_argument(
        "--format", "-f", choices=["json", "csv"], default="json", help="Format ispisa"
    )

    sub = parser.add_subparsers(dest="resource", required=True)

    # --- projekt (projekti-api) ---
    p = sub.add_parser("projekt", help="Projekti (projekti-api)")
    p.add_argument("--id", type=int)
    p.add_argument("--mbu")
    p.set_defaults(func=cmd_projekt)

    # --- osoba (projekti-api) ---
    p = sub.add_parser("osoba", help="Osobe (projekti-api)")
    p.add_argument("--id", type=int)
    p.add_argument("--oib")
    p.add_argument("--projekt-id", dest="projekt_id", type=int)
    p.set_defaults(func=cmd_osoba)

    # --- ustanova (projekti-api) ---
    p = sub.add_parser("ustanova", help="Ustanove (projekti-api)")
    p.add_argument("--id", type=int)
    p.add_argument("--projekt-id", dest="projekt_id", type=int)
    p.set_defaults(func=cmd_ustanova)

    # --- mozvag (projekti-api) ---
    p = sub.add_parser("mozvag", help="MOZVAG agregirani podaci (projekti-api)")
    ms = p.add_subparsers(dest="cmd", required=True)
    ms.add_parser("ustanove")
    ms.add_parser("financijeri")
    pp = ms.add_parser("projekti")
    pp.add_argument("--ustanova-id", dest="ustanova_id", type=int, required=True)
    pp.add_argument("--godina", type=int, required=True)
    po = ms.add_parser("osoba")
    po.add_argument("--mbz")
    po.add_argument("--oib")
    po.add_argument("--ustanova-id", dest="ustanova_id", type=int)
    po.add_argument("--godina", type=int, required=True)
    p.set_defaults(func=cmd_mozvag)

    # --- upisnik (ustanove-api) ---
    p = sub.add_parser("upisnik", help="MZO upisnik ustanova i PPG (ustanove-api)")
    us = p.add_subparsers(dest="cmd", required=True)
    us.add_parser("sve", help="Sve aktivne ustanove")
    us.add_parser("znanstvene", help="Znanstvene ustanove")
    us.add_parser("visoka-ucilista", help="Visoka učilišta")
    us.add_parser("jzi", help="Javni znanstveni instituti")
    us.add_parser("neaktivne", help="Neaktivne ustanove")
    us.add_parser("ppg", help="PPG područja")
    pi = us.add_parser("id", help="Ustanova po ID-u")
    pi.add_argument("ustanova_id", type=int)
    pm = us.add_parser("mbu", help="Ustanova po MBU kodu")
    pm.add_argument("mbu_kod")
    p.set_defaults(func=cmd_upisnik)

    # --- crosbi (crosbi-api) ---
    p = sub.add_parser("crosbi", help="CROSBI bibliografske publikacije (crosbi-api)")
    p.add_argument("--id", type=int)
    p.add_argument("--osoba-id", dest="osoba_id", type=int)
    p.add_argument("--mbz")
    p.add_argument("--projekt-id", dest="projekt_id", type=int)
    p.add_argument("--ustanova-id", dest="ustanova_id", type=int)
    p.set_defaults(func=cmd_crosbi)

    # --- oprema (oprema-api) ---
    p = sub.add_parser("oprema", help="Oprema i usluge (oprema-api)")
    p.add_argument("--id", type=int, help="ID opreme")
    p.add_argument("--usluga-id", dest="usluga_id", type=int)
    p.add_argument("--usluge", dest="list_usluge", action="store_true")
    p.set_defaults(func=cmd_oprema)

    # --- casopisi (casopisi-api) ---
    p = sub.add_parser("casopisi", help="Časopisi (casopisi-api)")
    p.add_argument("--id", type=int)
    p.set_defaults(func=cmd_casopisi)

    # --- dogadanja (dogadanja-api) ---
    p = sub.add_parser("dogadanja", help="Događanja (dogadanja-api)")
    p.add_argument("--id", type=int)
    p.set_defaults(func=cmd_dogadanja)

    # --- znanstvenici (znanstvenici-api) ---
    p = sub.add_parser("znanstvenici", help="Znanstvenici (znanstvenici-api)")
    p.add_argument("--oib")
    p.add_argument("--mbz")
    p.add_argument("--akreditacije-org-id", dest="akreditacije_org_id", type=int,
                   help="Akreditacije nastavnika za org. jedinicu")
    p.set_defaults(func=cmd_znanstvenici)

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
