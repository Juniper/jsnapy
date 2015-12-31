import logging


class XmlComparator:

    def __init__(self):
        self.logger_xml = logging.getLogger(__name__)
        self.tresult = {}
        self.tresult['result'] = True

    def text_compare(self, text1, text2):
        if not text1 and not text2:
            return True
        if text1 == '*' or text2 == '*':
            return True
        return (text1 or '').strip() == (text2 or '').strip()

    def xml_compare(self, x1, x2, buffer):
        flag = True
        if x1.tag != x2.tag:
            flag = False
            self.tresult['diff_on'] = "Tags"
            self.tresult['pre_node_tag'] = x1.tag
            self.tresult['post_node_tag'] = x2.tag
            self.tresult['result'] = flag
            self.tresult['testoperation'] = "simple-diff"
            buffer(
                "Tags do not match: \n   Pre: <%s>    Post: <%s>" %
                (x1.tag, x2.tag))

        for name, value in x1.attrib.items():
            if x2.attrib.get(name) != value:
                flag = False
                self.tresult['diff_on'] = "Attributes"
                self.tresult['pre_node_tag'] = x1.tag
                self.tresult['post_node_tag'] = x2.tag
                self.tresult['result'] = flag
                self.tresult['testoperation'] = "simple-diff"
                self.tresult['element'] = x1.tag
                buffer("Attributes do not match:\n %s=%r, %s=%r for tag values <%s>"
                       % (name, value, name, x2.attrib.get(name), x1.tag))

        for name in x1.attrib.keys():
            if name not in x2.attrib.keys():
                flag = False
                self.tresult['diff_on'] = "Attributes"
                self.tresult['pre_node_tag'] = x1.tag
                self.tresult['post_node_tag'] = x2.tag
                self.tresult['result'] = flag
                self.tresult['testoperation'] = "simple-diff"
                self.tresult['element'] = x1.tag
                buffer("Attribute missing in Post snap:\n <%s> for tag value <%s>"
                       % (name, x1.tag))

        for name, value in x2.attrib.items():
            if x1.attrib.get(name) != value:
                flag = False
                self.tresult['diff_on'] = "Attributes"
                self.tresult['pre_node_tag'] = x1.tag
                self.tresult['post_node_tag'] = x2.tag
                self.tresult['result'] = flag
                self.tresult['testoperation'] = "simple-diff"
                self.tresult['element'] = x1.tag

                buffer("Attributes do not match:\n %s=%r, %s=%r for tag values <%s>"
                       % (name, value, name, x1.attrib.get(name), x2.tag))

        for name in x2.attrib.keys():
            if name not in x1.attrib.keys():
                flag = False
                self.tresult['diff_on'] = "Attributes"
                self.tresult['pre_node_tag'] = x1.tag
                self.tresult['post_node_tag'] = x2.tag
                self.tresult['result'] = flag
                self.tresult['testoperation'] = "simple-diff"
                self.tresult['element'] = x1.tag

                buffer("Attribute missing in Pre snap:\n <%s> for tag value <%s>"
                       % (name, x2.tag))

        if not self.text_compare(x1.text, x2.text):
            flag = False
            self.tresult['diff_on'] = "Value different"
            self.tresult['element'] = x1.tag
            self.tresult['pre_node_value'] = x1.text
            self.tresult['post_node_value'] = x2.text
            self.tresult['result'] = flag
            self.tresult['testoperation'] = "simple-diff"

            if x1.getparent() is not None:
                self.tresult ['parent_node'] = x1.getparent().tag
                buffer(
                    "<%s> value different: \n    Pre node text: %r    Post node text: %r    Parent node: <%s>" %
                    (x1.tag, x1.text, x2.text, x1.getparent().tag))
            else:
                self.tresult ['parent_node'] = None
                buffer(
                    "<%s> value different: \n    Pre node text: %r    Post node text: %r" %
                    (x1.tag, x1.text, x2.text))
            print "flag is :", flag

        if not self.text_compare(x1.tail, x2.tail):
            flag = False
            self.tresult['diff_on'] = "Tail different"
            self.tresult['element'] = x1.tag
            self.tresult['pre_node_value'] = x1.tail
            self.tresult['post_node_value'] = x2.tail
            self.tresult['result'] = flag
            self.tresult['testoperation'] = "simple-diff"

            if x1.getparent() is not None:
                self.tresult ['parent_node'] = x1.getparent().tag
                buffer(
                    "<%s> tail value different: Pre node tail: %r    Post node tail: %r    Parent node: <%s>" %
                    (x1.tag, x1.tail, x2.tail, x1.getparent().tag))
            else:
                self.tresult ['parent_node'] = None
                buffer(
                    "<%s> tail value different: Pre node tail: %r    Post node tail: %r" %
                    (x1.tag, x1.tail, x2.tail))
            flag = False

        cl1 = x1.getchildren()
        cl2 = x2.getchildren()
        if len(cl1) != len(cl2):
            flag = False
            childlist1 = [val1.tag for val1 in cl1]
            childlist2 = [val2.tag for val2 in cl2]
            cval1 = [val1.tag for val1 in cl1 if val1.tag not in childlist2]
            cval2 = [val2.tag for val2 in cl2 if val2.tag not in childlist1]
            self.tresult['diff_on'] = "child_nodes_number"
            self.tresult['element'] = x1.tag
            self.tresult['pre_node_no'] = len(cl1)
            self.tresult['post_node_no'] = len(cl2)
            self.tresult['result'] = flag
            self.tresult['testoperation'] = "simple-diff"

            if len(cval1):
                self.tresult["missing_nodes_in_post"] = ','.join(cval1)
                buffer("No of child nodes for tag <%s> differs\n   Pre_no: %i    Post_no: %i \n   Missing nodes in post snapshots: <%s>"
                       % (x1.tag, len(cl1), len(cl2), ','.join(cval1)))

            if len(cval2):
                self.tresult["missing_nodes_in_pre"] = ','.join(cval2)
                buffer("No of child nodes for tag <%s> differs\n   Pre_no: %i    Post_no: %i \n   Missing nodes in pre snapshots: <%s>"
                       % (x1.tag, len(cl1), len(cl2), ','.join(cval2)))

        for c1, c2 in zip(cl1, cl2):
            if not self.xml_compare(c1, c2, buffer):
                flag = False
        if (flag is False):
            print "value of flag is:", flag
            return self.tresult
        else:
            return  self.tresult