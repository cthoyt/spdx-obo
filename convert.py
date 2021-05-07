# -*- coding: utf-8 -*-

"""Convert the SPDX license list to OBO."""

import click
import pathlib
import requests
from more_click import verbose_option
from typing import Any, Iterable, Mapping

from pyobo.struct import Obo, Reference, Term

HERE = pathlib.Path(__file__).parent.resolve()
URL = 'https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json'
PREFIX = 'spdx'


def get_data():
    res = requests.get(URL)
    res_json = res.json()
    data_version = res_json['licenseListVersion']
    entries = res_json['licenses']
    return data_version, entries


def iter_terms(entries: Iterable[Mapping[str, Any]]) -> Iterable[Term]:
    for entry in entries:
        try:
            term = entry_to_term(entry)
        except KeyError:
            click.secho(f'problem with: {entry}')
            raise
            continue
        else:
            yield term


def entry_to_term(entry: Mapping[str, Any]) -> Term:
    """
    :param entry:
    :return:

    Example::

    .. code-block:: javascript

        {
          "reference": "https://spdx.org/licenses/DOC.html",
          "isDeprecatedLicenseId": false,
          "detailsUrl": "https://spdx.org/licenses/DOC.json",
          "referenceNumber": 0,
          "name": "DOC License",
          "licenseId": "DOC",
          "seeAlso": [
            "http://www.cs.wustl.edu/~schmidt/ACE-copying.html",
            "https://www.dre.vanderbilt.edu/~schmidt/ACE-copying.html"
          ],
          "isOsiApproved": false
        }
    """
    term = Term(
        reference=Reference(
            prefix=PREFIX,
            identifier=entry['licenseId'],
            name=entry['name'],
        ),
        is_obsolete=entry['isDeprecatedLicenseId'],
    )
    for key in ['isOsiApproved', 'isFsfLibre']:
        value = entry.get(key)
        if value is not None:
            term.append_property(key,value)
    return term


@click.command()
@verbose_option
def main():
    data_version, entries = get_data()
    obo = Obo(
        name='Software Package Data Exchange',
        ontology=PREFIX,
        data_version=data_version,
        iter_terms=iter_terms,
        iter_terms_kwargs=dict(entries=entries)
    )
    obo.write_obo(HERE.joinpath(PREFIX).with_suffix('.obo'))


if __name__ == '__main__':
    main()
