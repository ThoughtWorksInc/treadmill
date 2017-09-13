from treadmill.infra import vpc, subnet
import click
import re
import pkg_resources

_IPA_PASSWORD_RE = re.compile('.{8,}')


def convert_to_vpc_id(ctx, param, value):
    """Returns VPC ID from Name"""
    if not value:
        return value

    try:
        return vpc.VPC.get_id_from_name(value)
    except ValueError as ex:
        raise click.BadParameter(ex.__str__())


def validate_vpc_name(ctx, param, value):
    _vpc_id = vpc.VPC.get_id_from_name(value)
    if _vpc_id:
        raise click.BadParameter(
            'VPC %s already exists with name: %s' %
            (_vpc_id, value)
        )
    else:
        return value


def validate_ipa_password(ctx, param, value):
    """IPA admin password valdiation"""
    value = value or click.prompt(
        'IPA admin password ', hide_input=True, confirmation_prompt=True
    )
    if not _IPA_PASSWORD_RE.match(value):
        raise click.BadParameter(
            'Password must be greater than 8 characters.'
        )
    return value


def validate_domain(ctx, param, value):
    """Cloud domain validation"""

    if value.count(".") != 1:
        raise click.BadParameter('Valid domain like example.com')

    return value


def ipa_password_prompt(ctx, param, value):
    """IPA admin password prompt"""
    return value or click.prompt('IPA admin password ', hide_input=True)


def current_release_version(ctx, param, value):
    """Treadmill current release version"""
    version = None

    try:
        version = pkg_resources.resource_string(
            'treadmill',
            'VERSION.txt'
        )
    except Exception:
        pass

    if version:
        return version.decode('utf-8').strip()
    else:
        raise click.BadParameter('No version specified in VERSION.txt')


def convert_to_subnet_id(vpc_id, subnet_name):
    if not subnet_name:
        return subnet_name
    subnet_id = subnet.Subnet.get_subnet_id_from_name(vpc_id, subnet_name)
    if not subnet_id:
        raise click.BadParameter("Subnet doesn't exist.")
    return subnet_id
