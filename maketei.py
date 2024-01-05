from datetime import datetime
from acdh_tei_pyutils.tei import TeiReader
from lxml import etree as ET
from lxml.etree import XMLSyntaxError
import json
import os
import re
import pandas as pd


nsmap = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "mets": "http://www.loc.gov/METS/",
    "mods": "http://www.loc.gov/mods/v3",
    "dv": "http://dfg-viewer.de/",
    "default": "http://www.tei-c.org/ns/1.0",
}

with open("data.json", "r") as f:
    data = json.load(f)

locdict = data["locations"]
bookdict = data["booktypes"]
persdict = data["persons"]


class Log:
    def __init__(self, logfile, stdout=False):
        if logfile:
            self.file_name = logfile
        else:
            self.file_name = False
        self.stdout = stdout

    def print_log(self, faulty_item, arg="could not be parsed", stdout=False):
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        log_entry = f"{faulty_item}: {arg}"
        if stdout:
            print(log_entry)
        if self.file_name:
            with open(f"{self.file_name}.log", "a") as f:
                f.write(f"{now}\t{log_entry}\n")


log = Log("0mets2tei")


class TeiTree:
    def __init__(self, source_table, source_tkb):
        self.filename = source_tkb
        self.tablename = source_table
        self.doc_id = os.path.basename(source_tkb).rstrip(".xml")
        self.tkb = self.read_xml_input(source_tkb)
        self.tkb = self.amend_pics_url(self.tkb, self.doc_id)
        self.tei = self.read_xml_input("template.xml")
        self.root = self.tei.any_xpath("//tei:TEI")[0]
        self.header = self.tei.any_xpath("//tei:teiHeader")[0]
        self.msdesc = self.tei.any_xpath("//tei:msDesc")[0]
        self.elements = self.extract_from_table(source_table, self.header)
        self.root.append(self.tkb.any_xpath("//tei:facsimile")[0])
        self.root.append(self.tkb.any_xpath("//tei:text")[0])
        self.make_text()
        self.printable = self.make_printable(self.tei.tree)

    @staticmethod
    def make_printable(tree):
        parser = ET.XMLParser(remove_blank_text=True)
        string = ET.tostring(tree, pretty_print=True, encoding="unicode")
        xml = ET.fromstring(string, parser=parser)
        return ET.tostring(xml, pretty_print=True, encoding="unicode")

    @staticmethod
    def amend_pics_url(tree, doc_id):
        graphic_elements = tree.any_xpath(".//tei:graphic")
        for element in graphic_elements:
            img_name = element.attrib["url"].split(".")[0].replace("Gu", "Gf")
            img_name = re.sub(r"^[\d_]*", "", img_name)
            element.attrib["url"] = (
                "https://viewer.acdh.oeaw.ac.at/viewer/api/v1/records/"
                f"{doc_id}/files/images/{img_name}/full/full/0/default.jpg"
            )
            for empty_url in tree.any_xpath(".//tei:graphic[@url='']"):
                empty_url.getparent().remove(empty_url)
        # e.g. https://viewer.acdh.oeaw.ac.at/viewer/content/A67_17/800/0/A-Gf_A67_17-012v.jpg
        return tree

    @staticmethod
    def read_xml_input(input_file):
        try:
            tree = TeiReader(input_file)
        except XMLSyntaxError as e:
            log.print_log(input_file, e, True)
            tree = False
        return tree

    @staticmethod
    def read_table(table):
        try:
            df = pd.read_csv(table).fillna("")
        except Exception:
            try:
                df = pd.read_excel(table).fillna("")
            except Exception:
                log.print_log(table, "Unsupported format", True)
        return df

    def extract_from_table(self, table, header):
        self.header = header
        df = self.read_table(table)
        column_name = self.doc_id[0] + " " + self.doc_id[1:].replace("_", "/")

        for idx, row in df.loc[df["Signatur"] == column_name].iterrows():
            self.parse_signature(row["Signatur"])
            self.parse_origin(row["Provenienz"], row["Drucker"])
            self.parse_date(str(row["Zeit"]))
            keys = self.classify_books(row["Buchtyp"], row["Liturgie"])
            self.parse_summary(row["Inhalt"], row["Buchtyp"], keys, idx)
            self.parse_extension(row["Umfang fol."])
            self.parse_format(row["Format"])
            self.parse_notation(False)  # Placeholder

    def parse_signature(self, sign):
        # sign = sign.replace("/", "_").replace(" ", "")
        self.msdesc.xpath("//tei:msIdentifier/tei:idno", namespaces=nsmap)[
            0
        ].text = sign
        if not self.header.xpath("//tei:titleStmt/tei:title", namespaces=nsmap)[0].text:
            self.header.xpath("//tei:titleStmt/tei:title", namespaces=nsmap)[
                0
            ].text = sign

    def parse_origin(self, origin, publisher=False):
        tree = self.tei.any_xpath(".//tei:standOff/tei:listPlace")[0]
        origins = origin.split(",")
        if origins[0]:
            place = ET.SubElement(tree, "place")
            if "?" in origins[0]:
                cert = True
            else:
                cert = False
            origins[0] = origins[0].strip("? ")
            dictentry = locdict[origins[0]]
            place.attrib[
                "{http://www.w3.org/XML/1998/namespace}id"
            ] = f"{dictentry['id']}"
            ET.SubElement(place, "placeName").text = origins[0]
            location = ET.SubElement(place, "location")
            ET.tostring(location, pretty_print=True, encoding="unicode")
            for i in dictentry["location"]:
                ET.SubElement(location, i).text = dictentry["location"][i]
            provenance = self.msdesc.xpath(
                "./tei:history/tei:provenance", namespaces=nsmap
            )[0]
            placename = ET.SubElement(provenance, "placeName")
            placename.text = origins[0]
            placename.attrib["ref"] = f"#{dictentry['id']}"
            if cert:
                placename.attrib["cert"] = "medium"
            if publisher:
                self.make_publisher(
                    ET.fromstring(
                        ET.tostring(placename, pretty_print=True, encoding="unicode")
                    ),
                    publisher,
                )
        if len(origins) > 1 and origins[1].strip("? ") in locdict:
            self.parse_origin(",".join(origins[1:]))

    def make_publisher(self, place, publisher):
        tree = ET.SubElement(self.tei.any_xpath(".//tei:standOff")[0], "listPerson")
        dictentry = persdict[publisher]
        person = ET.SubElement(tree, "person")
        for att in dictentry["attr"]:
            person.attrib[att] = dictentry["attr"][att]
        person.attrib["{http://www.w3.org/XML/1998/namespace}id"] = publisher.lower()
        for att in dictentry["data"]:
            ET.SubElement(person, att).text = dictentry["data"][att]
        bibl = self.header.xpath(
            "//tei:fileDesc/tei:sourceDesc/tei:bibl", namespaces=nsmap
        )[0]
        ET.SubElement(bibl, "pubPlace").append(place)
        pub = ET.SubElement(bibl, "publisher")
        pub.text = publisher.strip()
        pub.attrib["ref"] = f"#{publisher.lower()}"
        self.msdesc.xpath("//tei:physDesc/tei:objectDesc", namespaces=nsmap)[0].attrib[
            "form"
        ] = "print"
        self.header.xpath(
            "//tei:profileDesc/tei:textDesc/tei:channel", namespaces=nsmap
        )[0].text = "book"

    def parse_date(self, date):
        element = self.msdesc.xpath(
            "//tei:fileDesc/tei:sourceDesc/tei:bibl/tei:date", namespaces=nsmap
        )[0]
        try:
            year = re.sub("x+", "00", date).lstrip("~").split()[0]
            year = int(year.split("-")[0].strip("."))
        except Exception:
            log.print_log(self.tablename, f"“{date}”´ is not a valid date")
            year = "2023"
        if year == 2023:
            ddate = {"notBefore": "1000", "notAfter": year}
        elif date.startswith("~"):
            ddate = {"notBefore": f"{year - 20}", "notAfter": f"{year + 20}"}
        elif date.endswith("Jh.") or re.match(r"^\d{2}$", date):
            ddate = {
                "notBefore": f"{(year - 1) * 100}",
                "notAfter": f"{(year - 1) * 100 + 99}",
            }
        elif date.endswith("x"):
            ddate = {"notBefore": f"{year}", "notAfter": f"{year + 99}"}
        elif re.findall(r"^\d{2}\-\d(?:/\d)*", date):
            second = date.split("-")[1]
            year *= 100
            if second in "12":
                factor = int(100 / int(second))
                ddate = {"notBefore": year - factor, "notAfter": year - factor + 50}
            else:
                factor = int(
                    int(second.split("/")[0]) * 100 / int(second.split("/")[1])
                )
                ddate = {"notBefore": year + factor - 25, "notAfter": year + factor}
        else:
            ddate = {"when": f"{int(year)}"}
        element.text = date
        for time in ddate:
            element.attrib[time] = str(ddate[time])

    def classify_books(self, booktype, lit):
        taxonomies = self.header.xpath(
            "./tei:encodingDesc/tei:classDecl/tei:taxonomy", namespaces=nsmap
        )
        if lit:
            keys = f"#{lit.lower()}"
            cat = ET.Element("category")
            cat.attrib["{http://www.w3.org/XML/1998/namespace}id"] = lit.lower()
            ET.SubElement(cat, "catDesc").text = lit
            taxonomies[1].append(cat)
        else:
            keys = ""
        books = " ".join(" ".join(booktype.split(",")).split("/")).split()
        for book in books:
            for booktype in bookdict:
                if booktype in book.lower() and bookdict[booktype] not in keys:
                    cat = ET.Element("category")
                    cat.attrib["{http://www.w3.org/XML/1998/namespace}id"] = bookdict[
                        booktype
                    ]
                    ET.SubElement(cat, "catDesc").text = book
                    taxonomies[0].append(cat)
                    keys += f" #{bookdict[booktype]}"
        return keys

    def parse_summary(self, summary, bookt, attributes, line):
        if summary != summary:
            summary = ""
        title = re.findall("„(.*)“", summary)
        summary = summary.replace("„", "<title>").replace("“", "</title>")
        element = self.msdesc.xpath("//tei:msContents", namespaces=nsmap)[0]
        element.attrib["class"] = attributes
        subelement = element.xpath("//tei:summary", namespaces=nsmap)[0]
        subelement.append(ET.fromstring(f"<p>{summary}</p>"))
        subelement.append(ET.fromstring(f"<p>{bookt}</p>"))
        if title:
            tistmt = self.header.xpath(
                "//tei:fileDesc/tei:titleStmt", namespaces=nsmap
            )[0]
            title, subtitle = self.parse_title(title[0])
            if subtitle:
                ET.SubElement(tistmt, "title", type="sub").text = subtitle
            if tistmt.xpath("//tei:title", namespaces=nsmap)[0].text:
                ET.SubElement(tistmt, "title", type="desc").text = tistmt.xpath(
                    "//tei:title", namespaces=nsmap
                )[0].text
            tistmt.xpath("//tei:title", namespaces=nsmap)[0].text = title

    @staticmethod
    def parse_title(title):
        title = title.split(":")
        if len(title) < 2:
            title += [False]
        return title[0], title[1]

    def parse_extension(self, umfang):
        tree = self.msdesc.xpath(
            "//tei:physDesc/tei:objectDesc/tei:supportDesc/tei:extent/tei:measure",
            namespaces=nsmap,
        )[0]
        tree.attrib["unit"] = "leaf"
        if isinstance(umfang, (int, float)):
            umfang = str(int(umfang))
            tree.attrib["quantity"] = umfang
        else:
            for i in umfang.split():
                if i.isnumeric():
                    tree.attrib["quantity"] = i
                    break
        tree.text = umfang

    def parse_format(self, size):
        tree = self.msdesc.xpath(
            "//tei:physDesc/tei:objectDesc/tei:supportDesc/tei:support/tei:dimensions",
            namespaces=nsmap,
        )[0]
        size = size.replace("*", "x").split("x")
        if len(size) < 2:
            if size:
                ET.SubElement(tree, "dim").text = size[0]
        else:
            ET.SubElement(tree, "height").text = size[0]
            ET.SubElement(tree, "width").text = size[1]

    def parse_notation(self, placeholder):
        # We don't have the source yet.
        tree = self.msdesc.xpath("//tei:physDesc/tei:musicNotation", namespaces=nsmap)[
            0
        ]
        tree.text = "Placeholder"
        return tree

    def make_text(self):
        # Stub to include later required divs or milestones if required
        text = self.root.xpath("./tei:text", namespaces=nsmap)[0]
        return text
