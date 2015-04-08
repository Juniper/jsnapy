class XmlComparator:

    def text_compare(self, text1, text2):
        if not text1 and not text2:
            return True
        if text1 == '*' or text2 == '*':
            return True
        return (text1 or '').strip() == (text2 or '').strip()

    def xml_compare(self, x1, x2, buffer):
        flag = True
        if x1.tag != x2.tag:
            buffer(
                "Tags do not match: \n   Pre: <%s>    Post: <%s>" %
                (x1.tag, x2.tag))
            flag = False

        for name, value in x1.attrib.items():
            if x2.attrib.get(name) != value:
                buffer("Attributes do not match:\n %s=%r, %s=%r for tag values <%s>"
                       % (name, value, name, x2.attrib.get(name), x1.tag))
                flag = False

        for name in x1.attrib.keys():
            if name not in x2.attrib.keys():
                buffer("Attribute missing in Post snap:\n <%s> for tag value <%s>"
                       % (name, x1.tag))
                flag = False

        for name, value in x2.attrib.items():
            if x1.attrib.get(name) != value:
                buffer("Attributes do not match:\n %s=%r, %s=%r for tag values <%s>"
                       % (name, value, name, x1.attrib.get(name), x2.tag))
                flag = False

        for name in x2.attrib.keys():
            if name not in x1.attrib.keys():
                buffer("Attribute missing in Post snap:\n <%s> for tag value <%s>"
                       % (name, x2.tag))
                flag = False

        if not self.text_compare(x1.text, x2.text):
            if x1.getparent() is not None:
                buffer(
                    "<%s> value different: \n    Pre node text: %r    Post node text: %r    Parent node: <%s>" %
                    (x1.tag, x1.text, x2.text, x1.getparent().tag))
            else:
                buffer(
                    "<%s> value different: \n    Pre node text: %r    Post node text: %r" %
                    (x1.tag, x1.text, x2.text))
            flag = False

        if not self.text_compare(x1.tail, x2.tail):
            if x1.getparent() is not None:
                buffer(
                    "<%s> tail value different: Pre node tail: %r    Post node tail: %r    Parent node: <%s>" %
                    (x1.tag, x1.tail, x2.tail, x1.getparent().tag))
            else:
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
            if len(cval1):
                buffer("No of child nodes for tag <%s> differs\n   Pre_no: %i    Post_no: %i \n   Missing nodes in post snapshots: <%s>"
                       % (x1.tag, len(cl1), len(cl2), ','.join(cval1)))
            if len(cval2):
                buffer("No of child nodes for tag <%s> differs\n   Pre_no: %i    Post_no: %i \n   Missing nodes in pre snapshots: <%s>"
                       % (x1.tag, len(cl1), len(cl2), ','.join(cval2)))

        for c1, c2 in zip(cl1, cl2):
            if not self.xml_compare(c1, c2, buffer):
                flag = False
        if (flag is False):
            return False
        else:
            return True
