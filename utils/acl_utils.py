from collections import defaultdict
from pathlib import Path, PurePath
from itertools import product
from typing import List, Set, Dict
from argparse import ArgumentParser
import yaml
from sys import stdout
import json


def canonicalize(paths: List[Path], collapse: bool = True) -> Set[Path] | Dict[Path, Path]:
    """
        Canonicalizes a list of paths so that only the shortest paths are included
    """
    paths = [PurePath(p) for p in paths]
    path_map = {k: v for k, v in product(paths, paths) if k.is_relative_to(v)}
    if collapse:
        return set({str(v) for v in path_map.values()})
    else:
        return path_map


def parse_acl(rules: List[dict], prefix: Path) -> Dict[str, List[Path]]:
    """
        Parses an ACL file and returns a map of rules for each member
    """
    acl_map = defaultdict(set)

    for rule in rules:
        members = rule.get('member', [])
        members = members if isinstance(members, list) else [members]
        rule_prefix = Path('/' + rule['prefix']).resolve().relative_to('/')
        for m in members:
            acl_map[m].add(rule_prefix)

    user_policy = {
        subject: list(canonicalize({prefix / p for p in path}))
        for subject, path in acl_map.items()
    }

    return user_policy


def merge_acl(acl_files: List[Path]) -> Dict[str, List[Path]]:
    """
        Generate a global ACL rule file from a list of rules
    """
    policy_global = defaultdict(set)

    def ensure_prefix(k): return k if Path(k).is_relative_to(
        prefix) else str(prefix / k.lstrip('/'))

    for file in acl_files:
        with file.open() as fp:
            prefix = Path('/') / Path('/'.join(file.stem.split('__')))
            policy = yaml.safe_load(fp)
            for k, v in policy.items():
                policy_global[k] = policy_global[k].union(
                    {str(ensure_prefix(p)) for p in v}
                )

    return {k: list(v) for k, v in policy_global.items()}


def main():
    parser = ArgumentParser(description='Process ACL YAML File')
    subparsers = parser.add_subparsers(
        help='sub-command help', required=True, dest='command')

    parse_cmd = subparsers.add_parser(
        'parse-acl',
        help='parse-acl help', description='Parse an ACL file'
    )
    parse_cmd.add_argument('--acl-file', type=Path, required=True)
    parse_cmd.add_argument('--acl-prefix', type=Path, required=True)

    merge_cmd = subparsers.add_parser(
        'merge-acl',
        help='merge-acl help', description='Merge an ACL file'
    )
    merge_cmd.add_argument('--acl-dir', type=Path, required=True)

    args, _ = parser.parse_known_args()

    if args.command == 'parse-acl':
        with args.acl_file.open() as fp:
            raw_policy = yaml.safe_load(fp)
            policy = parse_acl(raw_policy, Path('/') / args.acl_prefix)
            json.dump(policy, stdout, indent=2)

    elif args.command == 'merge-acl':
        acl_files = [Path(f) for f in args.acl_dir.glob('*.yaml')]
        print(args.acl_dir)
        policy = merge_acl(acl_files)
        json.dump(policy, stdout, indent=2)