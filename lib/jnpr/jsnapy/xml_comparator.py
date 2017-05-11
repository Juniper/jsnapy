#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import logging

class XmlComparator:

    def __init__(self):
        self.logger_xml = logging.getLogger(__name__)
        self.tresult = {}
        self.tresult['result'] = True
        self.tresult['diff_on'] = []
        self.tresult['testoperation'] = "simple-diff"

    def text_compare(self, text1, text2):
        if not text1 and not text2:
            return True
        if text1 == '*' or text2 == '*':
            return True
        return (text1 or '').strip() == (text2 or '').strip()

    def xml_compare(self, x1, x2, buffer):
        flag = True
        if x1.tag != x2.tag:
            res = {}
            flag = False
            res['pre_node_tag'] = x1.tag
            res['post_node_tag'] = x2.tag
            res['result'] = flag
            res['testop'] = "tags_miss_match"
            buffer(
                "Tags do not match: \n   Pre: <%s>    Post: <%s>" %
                (x1.tag, x2.tag))
            self.tresult['diff_on'].append(res)
            self.tresult['result'] = flag

        for name, value in list(x1.attrib.items()):
            res = {}
            if x2.attrib.get(name) != value:
                flag = False
                res['testop'] = "attribute_miss_match"
                res['pre_node_tag'] = x1.tag
                res['post_node_tag'] = x2.tag
                res['result'] = flag
                res['element'] = x1.tag
                buffer("Attributes do not match:\n %s=%r, %s=%r for tag values <%s>"
                       % (name, value, name, x2.attrib.get(name), x1.tag))
                self.tresult['diff_on'].append(res)
                self.tresult['result'] = flag

        for name in list(x1.attrib.keys()):
            res = {}
            if name not in list(x2.attrib.keys()):
                flag = False
                res['testop'] = "attribute_missing"
                res['pre_node_tag'] = x1.tag
                res['post_node_tag'] = x2.tag
                res['result'] = flag
                res['element'] = x1.tag
                buffer("Attribute missing in Post snap:\n <%s> for tag value <%s>"
                       % (name, x1.tag))
                self.tresult['diff_on'].append(res)
                self.tresult['result'] = flag

        for name, value in list(x2.attrib.items()):
            res = {}
            if x1.attrib.get(name) != value:
                flag = False
                res['testop'] = "attribute_miss_match"
                res['pre_node_tag'] = x1.tag
                res['post_node_tag'] = x2.tag
                res['result'] = flag
                res['element'] = x1.tag
                self.tresult['diff_on'].append(res)
                self.tresult['result'] = flag

                buffer("Attributes do not match:\n %s=%r, %s=%r for tag values <%s>"
                       % (name, value, name, x1.attrib.get(name), x2.tag))

        for name in list(x2.attrib.keys()):
            res = {}
            if name not in list(x1.attrib.keys()):
                flag = False
                res['pre_node_tag'] = x1.tag
                res['post_node_tag'] = x2.tag
                res['result'] = flag
                res['element'] = x1.tag
                res['testop'] = "attribute_miss_match"
                self.tresult['diff_on'].append(res)
                self.tresult['result'] = flag
                buffer("Attribute missing in Pre snap:\n <%s> for tag value <%s>"
                       % (name, x2.tag))

        if not self.text_compare(x1.text, x2.text):
            flag = False
            res = {}
            res['testop'] = "value_miss_match"
            res['element'] = x1.tag
            res['pre_node_value'] = x1.text
            res['post_node_value'] = x2.text
            res['result'] = flag

            if x1.getparent() is not None:
                res['parent_node'] = x1.getparent().tag
                buffer(
                    "<%s> value different: \n    Pre node text: %r    Post node text: %r    Parent node: <%s>" %
                    (x1.tag, x1.text, x2.text, x1.getparent().tag))
            else:
                res['parent_node'] = None
                buffer(
                    "<%s> value different: \n    Pre node text: %r    Post node text: %r" %
                    (x1.tag, x1.text, x2.text))

            self.tresult['diff_on'].append(res)
            self.tresult['result'] = flag

        if not self.text_compare(x1.tail, x2.tail):
            flag = False
            res = {}
            res['testop'] = "tail_different"
            res['element'] = x1.tag
            res['pre_node_value'] = x1.tail
            res['post_node_value'] = x2.tail
            res['result'] = flag

            if x1.getparent() is not None:
                res['parent_node'] = x1.getparent().tag
                buffer(
                    "<%s> tail value different: Pre node tail: %r    Post node tail: %r    Parent node: <%s>" %
                    (x1.tag, x1.tail, x2.tail, x1.getparent().tag))
            else:
                res['parent_node'] = None
                buffer(
                    "<%s> tail value different: Pre node tail: %r    Post node tail: %r" %
                    (x1.tag, x1.tail, x2.tail))
            flag = False
            self.tresult['diff_on'].append(res)
            self.tresult['result'] = flag

        cl1 = x1.getchildren()
        cl2 = x2.getchildren()
        if len(cl1) != len(cl2):
            flag = False
            res = {}
            childlist1 = [val1.tag for val1 in cl1]
            childlist2 = [val2.tag for val2 in cl2]
            cval1 = [val1.tag for val1 in cl1 if val1.tag not in childlist2]
            cval2 = [val2.tag for val2 in cl2 if val2.tag not in childlist1]
            res['testop'] = "child_node_miss_match"
            res['element'] = x1.tag
            res['pre_node_no'] = len(cl1)
            res['post_node_no'] = len(cl2)
            res['result'] = flag

            if len(cval1):
                res["missing_nodes_in_post"] = ','.join(cval1)
                buffer("No of child nodes for tag <%s> differs\n   Pre_no: %i    Post_no: %i \n   Missing nodes in post snapshots: <%s>"
                       % (x1.tag, len(cl1), len(cl2), ','.join(cval1)))

            if len(cval2):
                res["missing_nodes_in_pre"] = ','.join(cval2)
                buffer("No of child nodes for tag <%s> differs\n   Pre_no: %i    Post_no: %i \n   Missing nodes in pre snapshots: <%s>"
                       % (x1.tag, len(cl1), len(cl2), ','.join(cval2)))
            self.tresult['diff_on'].append(res)
            self.tresult['result'] = flag

        for c1, c2 in zip(cl1, cl2):
            if not self.xml_compare(c1, c2, buffer):
                flag = False
                self.tresult['result'] = flag
        return self.tresult
