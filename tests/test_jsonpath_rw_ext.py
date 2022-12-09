# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_bc_jsonpath_ng_ext
----------------------------------

Tests for `bc_jsonpath_ng_ext` module.
"""
import pytest

from bc_jsonpath_ng import jsonpath  # For setting the global auto_id_field flag
from oslotest import base
import testscenarios

from bc_jsonpath_ng.ext import parser


@pytest.mark.parametrize(
    "query,data,expected",
    [
        (
            "objects.`sorted`",
            {"objects": ["alpha", "gamma", "beta"]},
            [["alpha", "beta", "gamma"]],
        ),
        (
            "objects.`sorted`[1]",
            {"objects": ["alpha", "gamma", "beta"]},
            "beta",
        ),
        (
            "objects.`sorted`",
            {"objects": {"cow": "moo", "horse": "neigh", "cat": "meow"}},
            [["cat", "cow", "horse"]],
        ),
        (
            "objects.`sorted`[0]",
            {"objects": {"cow": "moo", "horse": "neigh", "cat": "meow"}},
            "cat",
        ),
        (
            "objects.`len`",
            {"objects": ["alpha", "gamma", "beta"]},
            3,
        ),
        (
            "objects.`len`",
            {"objects": {"cow": "moo", "cat": "neigh"}},
            2,
        ),
        (
            "objects[0].`len`",
            {"objects": ["alpha", "gamma"]},
            5,
        ),
        (
            "objects[?cow]",
            {"objects": [{"cow": "moo"}, {"cat": "neigh"}]},
            [{"cow": "moo"}],
        ),
        (
            "objects[?@.cow]",
            {"objects": [{"cow": "moo"}, {"cat": "neigh"}]},
            [{"cow": "moo"}],
        ),
        (
            "objects[?(@.cow)]",
            {"objects": [{"cow": "moo"}, {"cat": "neigh"}]},
            [{"cow": "moo"}],
        ),
        (
            'objects[?(@."cow!?cat")]',
            {"objects": [{"cow!?cat": "moo"}, {"cat": "neigh"}]},
            [{"cow!?cat": "moo"}],
        ),
        (
            'objects[?cow="moo"]',
            {"objects": [{"cow": "moo"}, {"cow": "neigh"}, {"cat": "neigh"}]},
            [{"cow": "moo"}],
        ),
        (
            'objects[?(@.["cow"]="moo")]',
            {"objects": [{"cow": "moo"}, {"cow": "neigh"}, {"cat": "neigh"}]},
            [{"cow": "moo"}],
        ),
        (
            'objects[?cow=="moo"]',
            {"objects": [{"cow": "moo"}, {"cow": "neigh"}, {"cat": "neigh"}]},
            [{"cow": "moo"}],
        ),
        (
            "objects[?cow>5]",
            {"objects": [{"cow": 8}, {"cow": 7}, {"cow": 5}, {"cow": "neigh"}]},
            [{"cow": 8}, {"cow": 7}],
        ),
        (
            "objects[?cow>5&cat=2]",
            {
                "objects": [
                    {"cow": 8, "cat": 2},
                    {"cow": 7, "cat": 2},
                    {"cow": 2, "cat": 2},
                    {"cow": 5, "cat": 3},
                    {"cow": 8, "cat": 3},
                ]
            },
            [{"cow": 8, "cat": 2}, {"cow": 7, "cat": 2}],
        ),
        (
            "objects[?confidence>=0.5].prediction",
            {
                "objects": [
                    {"confidence": 0.42, "prediction": "Good"},
                    {"confidence": 0.58, "prediction": "Bad"},
                ]
            },
            ["Bad"],
        ),
        (
            "objects[/cow]",
            {
                "objects": [
                    {"cat": 1, "cow": 2},
                    {"cat": 2, "cow": 1},
                    {"cat": 3, "cow": 3},
                ]
            },
            [[{"cat": 2, "cow": 1}, {"cat": 1, "cow": 2}, {"cat": 3, "cow": 3}]],
        ),
        (
            "objects[/cow][0].cat",
            {
                "objects": [
                    {"cat": 1, "cow": 2},
                    {"cat": 2, "cow": 1},
                    {"cat": 3, "cow": 3},
                ]
            },
            2,
        ),
        (
            "objects[\cat]",
            {"objects": [{"cat": 2}, {"cat": 1}, {"cat": 3}]},
            [[{"cat": 3}, {"cat": 2}, {"cat": 1}]],
        ),
        (
            "objects[\cat][-1].cat",
            {"objects": [{"cat": 2}, {"cat": 1}, {"cat": 3}]},
            1,
        ),
        (
            "objects[/cow,\cat]",
            {
                "objects": [
                    {"cat": 1, "cow": 2},
                    {"cat": 2, "cow": 1},
                    {"cat": 3, "cow": 1},
                    {"cat": 3, "cow": 3},
                ]
            },
            [
                [
                    {"cat": 3, "cow": 1},
                    {"cat": 2, "cow": 1},
                    {"cat": 1, "cow": 2},
                    {"cat": 3, "cow": 3},
                ]
            ],
        ),
        (
            "objects[/cow,\cat][0].cat",
            {
                "objects": [
                    {"cat": 1, "cow": 2},
                    {"cat": 2, "cow": 1},
                    {"cat": 3, "cow": 1},
                    {"cat": 3, "cow": 3},
                ]
            },
            3,
        ),
        (
            "objects[/cat.cow]",
            {
                "objects": [
                    {"cat": {"dog": 1, "cow": 2}},
                    {"cat": {"dog": 2, "cow": 1}},
                    {"cat": {"dog": 3, "cow": 3}},
                ]
            },
            [
                [
                    {"cat": {"dog": 2, "cow": 1}},
                    {"cat": {"dog": 1, "cow": 2}},
                    {"cat": {"dog": 3, "cow": 3}},
                ]
            ],
        ),
        (
            "objects[/cat.cow][0].cat.dog",
            {
                "objects": [
                    {"cat": {"dog": 1, "cow": 2}},
                    {"cat": {"dog": 2, "cow": 1}},
                    {"cat": {"dog": 3, "cow": 3}},
                ]
            },
            2,
        ),
        (
            "objects[/cat.(cow,bow)]",
            {
                "objects": [
                    {"cat": {"dog": 1, "bow": 3}},
                    {"cat": {"dog": 2, "cow": 1}},
                    {"cat": {"dog": 2, "bow": 2}},
                    {"cat": {"dog": 3, "cow": 2}},
                ]
            },
            [
                [
                    {"cat": {"dog": 2, "cow": 1}},
                    {"cat": {"dog": 2, "bow": 2}},
                    {"cat": {"dog": 3, "cow": 2}},
                    {"cat": {"dog": 1, "bow": 3}},
                ]
            ],
        ),
        (
            "objects[/cat.(cow,bow)][0].cat.dog",
            {
                "objects": [
                    {"cat": {"dog": 1, "bow": 3}},
                    {"cat": {"dog": 2, "cow": 1}},
                    {"cat": {"dog": 2, "bow": 2}},
                    {"cat": {"dog": 3, "cow": 2}},
                ]
            },
            2,
        ),
        (
            "3 * 3",
            {},
            [9],
        ),
        (
            "$.foo * 10",
            {"foo": 4},
            [40],
        ),
        (
            "10 * $.foo",
            {"foo": 4},
            [40],
        ),
        (
            "$.foo * 10",
            {"foo": 4},
            [40],
        ),
        (
            "$.foo * 3",
            {"foo": "f"},
            ["fff"],
        ),
        (
            "foo * 3",
            {"foo": "f"},
            ["foofoofoo"],
        ),
        (
            "($.foo * 10 * $.foo) + 2",
            {"foo": 4},
            [162],
        ),
        (
            "$.foo * 10 * $.foo + 2",
            {"foo": 4},
            [240],
        ),
        (
            "foo + bar",
            {"foo": "name", "bar": "node"},
            ["foobar"],
        ),
        (
            'foo + "_" + bar',
            {"foo": "name", "bar": "node"},
            ["foo_bar"],
        ),
        (
            '$.foo + "_" + $.bar',
            {"foo": "name", "bar": "node"},
            ["name_node"],
        ),
        (
            "$.foo + $.bar",
            {"foo": "name", "bar": "node"},
            ["namenode"],
        ),
        (
            "foo.cow + bar.cow",
            {"foo": {"cow": "name"}, "bar": {"cow": "node"}},
            ["namenode"],
        ),
        (
            "$.objects[*].cow * 2",
            {"objects": [{"cow": 1}, {"cow": 2}, {"cow": 3}]},
            [2, 4, 6],
        ),
        (
            "$.objects[*].cow * $.objects[*].cow",
            {"objects": [{"cow": 1}, {"cow": 2}, {"cow": 3}]},
            [1, 4, 9],
        ),
        (
            "$.objects[*].cow * $.objects2[*].cow",
            {
                "objects": [{"cow": 1}, {"cow": 2}, {"cow": 3}],
                "objects2": [{"cow": 5}],
            },
            [],
        ),
        (
            '$.objects * "foo"',
            {"objects": []},
            [],
        ),
        (
            '"bar" * "foo"',
            {},
            [],
        ),
        (
            "payload.metrics[?(@.name='cpu.frequency')].value * 100",
            {
                "payload": {
                    "metrics": [
                        {
                            "timestamp": "2013-07-29T06:51:34.472416",
                            "name": "cpu.frequency",
                            "value": 1600,
                            "source": "libvirt.LibvirtDriver",
                        },
                        {
                            "timestamp": "2013-07-29T06:51:34.472416",
                            "name": "cpu.user.time",
                            "value": 17421440000000,
                            "source": "libvirt.LibvirtDriver",
                        },
                    ]
                }
            },
            [160000],
        ),
        (
            "payload.(id|(resource.id))",
            {"payload": {"id": "foobar"}},
            ["foobar"],
        ),
        (
            "payload.id|(resource.id)",
            {"payload": {"resource": {"id": "foobar"}}},
            ["foobar"],
        ),
        (
            "payload.id|(resource.id)",
            {"payload": {"id": "yes", "resource": {"id": "foobar"}}},
            ["yes", "foobar"],
        ),
        (
            "payload.`sub(/(foo\\\\d+)\\\\+(\\\\d+bar)/, \\\\2-\\\\1)`",
            {"payload": "foo5+3bar"},
            ["3bar-foo5"],
        ),
        (
            "payload.`sub(/foo\\\\+bar/, repl)`",
            {"payload": "foo+bar"},
            ["repl"],
        ),
        (
            "payload.`str()`",
            {"payload": 1},
            ["1"],
        ),
        (
            "payload.`split(-, 2, -1)`",
            {"payload": "foo-bar-cat-bow"},
            ["cat"],
        ),
        (
            "payload.`split(-, 2, 2)`",
            {"payload": "foo-bar-cat-bow"},
            ["cat-bow"],
        ),
        (
            "foo[?(@.baz==1)]",
            {"foo": [{"baz": 1}, {"baz": 2}]},
            [{"baz": 1}],
        ),
        (
            "foo[*][?(@.baz==1)]",
            {"foo": [{"baz": 1}, {"baz": 2}]},
            [],
        ),
        (
            "foo[?flag = true].color",
            {
                "foo": [
                    {"color": "blue", "flag": True},
                    {"color": "green", "flag": False},
                ]
            },
            ["blue"],
        ),
        (
            "foo[?flag = false].color",
            {
                "foo": [
                    {"color": "blue", "flag": True},
                    {"color": "green", "flag": False},
                ]
            },
            ["green"],
        ),
        (
            "foo[?flag = true].color",
            {
                "foo": [
                    {"color": "blue", "flag": True},
                    {"color": "green", "flag": 2},
                    {"color": "red", "flag": "hi"},
                ]
            },
            ["blue"],
        ),
        (
            'foo[?flag = "true"].color',
            {
                "foo": [
                    {"color": "blue", "flag": True},
                    {"color": "green", "flag": "true"},
                ]
            },
            ["green"],
        ),
    ],
    ids=[
        "sorted_list",
        "sorted_list_indexed",
        "sorted_dict",
        "sorted_dict_indexed",
        "len_list",
        "len_dict",
        "len_str",
        "filter_exists_syntax1",
        "filter_exists_syntax2",
        "filter_exists_syntax3",
        "filter_exists_syntax4",
        "filter_eq1",
        "filter_eq2",
        "filter_eq3",
        "filter_gt",
        "filter_and",
        "filter_float_gt",
        "sort1",
        "sort1_indexed",
        "sort2",
        "sort2_indexed",
        "sort3",
        "sort3_indexed",
        "sort4",
        "sort4_indexed",
        "sort5_twofields",
        "sort5_indexed",
        "arithmetic_number_only",
        "arithmetic_mul1",
        "arithmetic_mul2",
        "arithmetic_mul3",
        "arithmetic_mul4",
        "arithmetic_mul5",
        "arithmetic_mul6",
        "arithmetic_mul7",
        "arithmetic_str0",
        "arithmetic_str1",
        "arithmetic_str2",
        "arithmetic_str3",
        "arithmetic_str4",
        "arithmetic_list1",
        "arithmetic_list2",
        "arithmetic_list_err1",
        "arithmetic_err1",
        "arithmetic_err2",
        "real_life_example1",
        "real_life_example2",
        "real_life_example3",
        "real_life_example4",
        "sub1",
        "sub2",
        "str1",
        "split1",
        "split2",
        "bug-#2-correct",
        "bug-#2-wrong",
        "boolean-filter-true",
        "boolean-filter-false",
        "boolean-filter-other-datatypes-involved",
        "boolean-filter-string-true-string-literal",
    ],
)
def test_jsonpath_ext(query, data, expected):
    jsonpath.auto_id_field = None
    result = parser.parse(query, debug=True).find(data)
    if isinstance(expected, list):
        assert [r.value for r in result] == expected
    elif isinstance(expected, set):
        assert {r.value for r in result} == expected
    else:
        assert result[0].value == expected


# NOTE(sileht): copy of tests/test_jsonpath.py
# to ensure we didn't break bc_jsonpath_ng


class TestJsonPath(base.BaseTestCase):
    """Tests of the actual jsonpath functionality"""

    #
    # Check that the data value returned is good
    #
    def check_cases(self, test_cases):
        # Note that just manually building an AST would avoid this dep and
        # isolate the tests, but that would suck a bit
        # Also, we coerce iterables, etc, into the desired target type

        for string, data, target in test_cases:
            print('parse("%s").find(%s) =?= %s' % (string, data, target))
            result = parser.parse(string).find(data)
            if isinstance(target, list):
                assert [r.value for r in result] == target
            elif isinstance(target, set):
                assert set([r.value for r in result]) == target
            else:
                assert result.value == target

    def test_fields_value(self):
        jsonpath.auto_id_field = None
        self.check_cases(
            [
                ("foo", {"foo": "baz"}, ["baz"]),
                ("foo,baz", {"foo": 1, "baz": 2}, [1, 2]),
                ("@foo", {"@foo": 1}, [1]),
                ("*", {"foo": 1, "baz": 2}, set([1, 2])),
            ]
        )

        jsonpath.auto_id_field = "id"
        self.check_cases([("*", {"foo": 1, "baz": 2}, set([1, 2, "`this`"]))])

    def test_root_value(self):
        jsonpath.auto_id_field = None
        self.check_cases(
            [
                ("$", {"foo": "baz"}, [{"foo": "baz"}]),
                ("foo.$", {"foo": "baz"}, [{"foo": "baz"}]),
                ("foo.$.foo", {"foo": "baz"}, ["baz"]),
            ]
        )

    def test_this_value(self):
        jsonpath.auto_id_field = None
        self.check_cases(
            [
                ("`this`", {"foo": "baz"}, [{"foo": "baz"}]),
                ("foo.`this`", {"foo": "baz"}, ["baz"]),
                ("foo.`this`.baz", {"foo": {"baz": 3}}, [3]),
            ]
        )

    def test_index_value(self):
        self.check_cases([("[0]", [42], [42]), ("[5]", [42], []), ("[2]", [34, 65, 29, 59], [29])])

    def test_slice_value(self):
        self.check_cases(
            [
                ("[*]", [1, 2, 3], [1, 2, 3]),
                ("[*]", range(1, 4), [1, 2, 3]),
                ("[1:]", [1, 2, 3, 4], [2, 3, 4]),
                ("[:2]", [1, 2, 3, 4], [1, 2]),
            ]
        )

        # Funky slice hacks
        self.check_cases(
            [
                ("[*]", 1, [1]),  # This is a funky hack
                ("[0:]", 1, [1]),  # This is a funky hack
                ("[*]", {"foo": 1}, [{"foo": 1}]),  # This is a funky hack
                ("[*].foo", {"foo": 1}, [1]),  # This is a funky hack
            ]
        )

    def test_child_value(self):
        self.check_cases(
            [
                ("foo.baz", {"foo": {"baz": 3}}, [3]),
                ("foo.baz", {"foo": {"baz": [3]}}, [[3]]),
                ("foo.baz.bizzle", {"foo": {"baz": {"bizzle": 5}}}, [5]),
            ]
        )

    def test_descendants_value(self):
        self.check_cases(
            [
                ("foo..baz", {"foo": {"baz": 1, "bing": {"baz": 2}}}, [1, 2]),
                ("foo..baz", {"foo": [{"baz": 1}, {"baz": 2}]}, [1, 2]),
            ]
        )

    def test_parent_value(self):
        self.check_cases(
            [
                ("foo.baz.`parent`", {"foo": {"baz": 3}}, [{"baz": 3}]),
                (
                    "foo.`parent`.foo.baz.`parent`.baz.bizzle",
                    {"foo": {"baz": {"bizzle": 5}}},
                    [5],
                ),
            ]
        )

    def test_hyphen_key(self):
        # NOTE(sileht): hyphen is now a operator
        # so to use it has key we must escape it with quote
        # self.check_cases([('foo.bar-baz', {'foo': {'bar-baz': 3}}, [3]),
        #                  ('foo.[bar-baz,blah-blah]',
        #                   {'foo': {'bar-baz': 3, 'blah-blah': 5}},
        #                   [3, 5])])
        self.check_cases(
            [
                ('foo."bar-baz"', {"foo": {"bar-baz": 3}}, [3]),
                (
                    'foo.["bar-baz","blah-blah"]',
                    {"foo": {"bar-baz": 3, "blah-blah": 5}},
                    [3, 5],
                ),
            ]
        )
        # self.assertRaises(lexer.JsonPathLexerError, self.check_cases,
        #                  [('foo.-baz', {'foo': {'-baz': 8}}, [8])])

    #
    # Check that the paths for the data are correct.
    # FIXME: merge these tests with the above, since the inputs are the same
    # anyhow
    #
    def check_paths(self, test_cases):
        # Note that just manually building an AST would avoid this dep and
        # isolate the tests, but that would suck a bit
        # Also, we coerce iterables, etc, into the desired target type

        for string, data, target in test_cases:
            print('parse("%s").find(%s).paths =?= %s' % (string, data, target))
            result = parser.parse(string).find(data)
            if isinstance(target, list):
                assert [str(r.full_path) for r in result] == target
            elif isinstance(target, set):
                assert set([str(r.full_path) for r in result]) == target
            else:
                assert str(result.path) == target

    def test_fields_paths(self):
        jsonpath.auto_id_field = None
        self.check_paths(
            [
                ("foo", {"foo": "baz"}, ["foo"]),
                ("foo,baz", {"foo": 1, "baz": 2}, ["foo", "baz"]),
                ("*", {"foo": 1, "baz": 2}, set(["foo", "baz"])),
            ]
        )

        jsonpath.auto_id_field = "id"
        self.check_paths([("*", {"foo": 1, "baz": 2}, set(["foo", "baz", "id"]))])

    def test_root_paths(self):
        jsonpath.auto_id_field = None
        self.check_paths(
            [
                ("$", {"foo": "baz"}, ["$"]),
                ("foo.$", {"foo": "baz"}, ["$"]),
                ("foo.$.foo", {"foo": "baz"}, ["foo"]),
            ]
        )

    def test_this_paths(self):
        jsonpath.auto_id_field = None
        self.check_paths(
            [
                ("`this`", {"foo": "baz"}, ["`this`"]),
                ("foo.`this`", {"foo": "baz"}, ["foo"]),
                ("foo.`this`.baz", {"foo": {"baz": 3}}, ["foo.baz"]),
            ]
        )

    def test_index_paths(self):
        self.check_paths([("[0]", [42], ["[0]"]), ("[2]", [34, 65, 29, 59], ["[2]"])])

    def test_slice_paths(self):
        self.check_paths(
            [
                ("[*]", [1, 2, 3], ["[0]", "[1]", "[2]"]),
                ("[1:]", [1, 2, 3, 4], ["[1]", "[2]", "[3]"]),
            ]
        )

    def test_child_paths(self):
        self.check_paths(
            [
                ("foo.baz", {"foo": {"baz": 3}}, ["foo.baz"]),
                ("foo.baz", {"foo": {"baz": [3]}}, ["foo.baz"]),
                ("foo.baz.bizzle", {"foo": {"baz": {"bizzle": 5}}}, ["foo.baz.bizzle"]),
            ]
        )

    def test_descendants_paths(self):
        self.check_paths(
            [
                (
                    "foo..baz",
                    {"foo": {"baz": 1, "bing": {"baz": 2}}},
                    ["foo.baz", "foo.bing.baz"],
                )
            ]
        )

    #
    # Check the "auto_id_field" feature
    #
    def test_fields_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases(
            [
                ("foo.id", {"foo": "baz"}, ["foo"]),
                ("foo.id", {"foo": {"id": "baz"}}, ["baz"]),
                ("foo,baz.id", {"foo": 1, "baz": 2}, ["foo", "baz"]),
                ("*.id", {"foo": {"id": 1}, "baz": 2}, set(["1", "baz"])),
            ]
        )

    def test_root_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases(
            [
                ("$.id", {"foo": "baz"}, ["$"]),  # This is a wonky case that is
                # not that interesting
                ("foo.$.id", {"foo": "baz", "id": "bizzle"}, ["bizzle"]),
                ("foo.$.baz.id", {"foo": 4, "baz": 3}, ["baz"]),
            ]
        )

    def test_this_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases(
            [
                ("id", {"foo": "baz"}, ["`this`"]),  # This is, again, a wonky case
                # that is not that interesting
                ("foo.`this`.id", {"foo": "baz"}, ["foo"]),
                ("foo.`this`.baz.id", {"foo": {"baz": 3}}, ["foo.baz"]),
            ]
        )

    def test_index_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases([("[0].id", [42], ["[0]"]), ("[2].id", [34, 65, 29, 59], ["[2]"])])

    def test_slice_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases(
            [
                ("[*].id", [1, 2, 3], ["[0]", "[1]", "[2]"]),
                ("[1:].id", [1, 2, 3, 4], ["[1]", "[2]", "[3]"]),
            ]
        )

    def test_child_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases(
            [
                ("foo.baz.id", {"foo": {"baz": 3}}, ["foo.baz"]),
                ("foo.baz.id", {"foo": {"baz": [3]}}, ["foo.baz"]),
                ("foo.baz.id", {"foo": {"id": "bizzle", "baz": 3}}, ["bizzle.baz"]),
                ("foo.baz.id", {"foo": {"baz": {"id": "hi"}}}, ["foo.hi"]),
                (
                    "foo.baz.bizzle.id",
                    {"foo": {"baz": {"bizzle": 5}}},
                    ["foo.baz.bizzle"],
                ),
            ]
        )

    def test_descendants_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases(
            [
                (
                    "foo..baz.id",
                    {"foo": {"baz": 1, "bing": {"baz": 2}}},
                    ["foo.baz", "foo.bing.baz"],
                )
            ]
        )
