
import json

from acl import parse_acl, merge_acl
from pathlib import Path
import yaml
import click
from click import Group

from upath import UPath

@click.command()
@click.option('--acl-path', required=True, help='Prefix to search for ACL definitions')
@click.option('--output-path', required=True, help='Path to output ACLs to')
def generate_global_acl(acl_path: Path, output_path: str):
    acl_files = [f for f in UPath(acl_path).glob('*.yaml')]
    policy = merge_acl(acl_files)
    with UPath(output_path).open('w') as fp:
        json.dump(policy, fp, indent=2)

@click.command()
@click.option('--acl-file', required=True, help='ACL file to parse')
@click.option('--acl-prefix', required=True, help='Prefix to search for ACL definitions')
@click.option('--output-path', required=True, help='Path to output ACL file')
def generate_local_acl(acl_file, acl_prefix, output_path):
    with UPath(acl_file).open() as fp:
        raw_policy = yaml.safe_load(fp)
        print(raw_policy)
    acl_prefix = Path('/') / acl_prefix
    output_path = UPath(output_path)
    policy = parse_acl(raw_policy, acl_prefix)
    with output_path.open('w') as fp:
        json.dump(policy, fp, indent=2)

if __name__ == '__main__':
    group = Group('acl', help='ACL commands', commands=[
        generate_global_acl,
        generate_local_acl
    ])
    group()