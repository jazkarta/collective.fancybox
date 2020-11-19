# -*- coding: utf-8 -*-
from collective.fancybox.testing import \
    COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING  # noqa: E501
from plone.testing import layered
from unittest import TestSuite

import doctest
import glob
import os
import re
import six


OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


class Py23DocChecker(doctest.OutputChecker):

    def check_output(self, want, got, optionflags):
        if six.PY2:
            want = re.sub('zExceptions.Forbidden', 'Forbidden', want)
            want = re.sub("b'(.*?)'", "'\\1'", want)
        else:
            want = re.sub("u'(.*?)'", "'\\1'", want)
            # translate doctest exceptions
            for dotted in ('urllib.error.HTTPError', ):
                if dotted in got:
                    got = re.sub(
                        dotted,
                        dotted.rpartition('.')[-1],
                        got,
                    )

        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    standard_filenames = [
        filename for filename in
        glob.glob(os.path.sep.join([os.path.dirname(__file__), '*.txt']))
    ]
    suites = [
        layered(
            doctest.DocFileSuite(
                os.path.basename(filename),
                optionflags=OPTIONFLAGS,
                package='collective.fancybox.tests',
                checker=Py23DocChecker(),
            ),
            layer=COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING
        ) for filename in standard_filenames
    ]

    return TestSuite(suites)
