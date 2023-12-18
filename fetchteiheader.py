#!/usr/bin/env python3
from datetime import datetime
from acdh_tei_pyutils.tei import TeiReader
from lxml import etree as ET
import json
import os
import re
import pandas as pd
from openpyxl import load_workbook


nsmap = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "mets": "http://www.loc.gov/METS/",
    "mods": "http://www.loc.gov/mods/v3",
    "dv": "http://dfg-viewer.de/",
}


class Log:
    def __init__(self, logfile):
        self.file_name = logfile

    def print_log(self, faulty_item, arg="could not be parsed"):
        now = datetime.now()
        with open(f"{self.file_name}.log", "a") as f:
            f.write(
                f'{now.strftime("%Y/%m/%d %H:%M:%S")}\t' f"File `{faulty_item}` {arg}\n"
            )


log = Log("mets2tei.log")


class Table:
    def __init__(self, source_table):
        self.elements = self.extract_from_table(source_table, {})

    def extract_from_table(self, table, elements):
        wb_obj = load_workbook(table).active
        df = pd.read_excel(table)
        df.fillna("", inplace=True)  # Fill empty cells with 0-length strings
        for idx, row in df.iterrows():
            name = row["Signatur"].replace("/", "_").replace(" ", "")
            elements[name] = {}
            elements[name]["Signature"] = self.parse_signature(row["Signatur"])
            book = self.classify_books(row["Buchtyp"])
            if row["Liturgie"] == row["Liturgie"]:  # In case of empty cell
                liturgy = f'#{row["Liturgie"].lower()}'
            else:
                liturgy = ""
            elements[name]["Origin"] = self.parse_origin(row["Provenienz"])
            elements[name]["Year"] = self.parse_date(str(row["Zeit"]))
            if row["Inhalt"] == row["Inhalt"]:  # In case of empty cell
                content = wb_obj.cell(row=idx + 1, column=6)
                # content = row["Inhalt"]
            else:
                content = ""
            elements[name]["Summary"] = self.parse_summary(
                content, " ".join([book, liturgy])
            )
            elements[name]["Extension"] = self.parse_extension(row["Umfang fol."])
            elements[name]["Format"] = self.parse_format(row["Format"])
            elements[name]["Device"] = row["Gerät"]
            elements[name]["Pictures"] = row["Bilder"]
            elements[name]["Notation"] = self.parse_notation(False)  # Placeholder
        return elements

    @staticmethod
    def classify_books(booktype):
        books = " ".join(" ".join(booktype.split(",")).split("/")).split()
        keys = ""
        with open("booktypes.json", "r") as f:
            dictionary = json.load(f)
        for book in books:
            for booktype in dictionary.values():
                if booktype in book:
                    keys += f" #{dictionary[booktype]}"
        return keys

    @staticmethod
    def parse_origin(origin):
        # it's probably the place of production rather than the archive. It must go somewhere else...
        tree = ET.Element("repository")
        tree.text = origin
        return tree

    @staticmethod
    def parse_date(date):
        try:
            year = re.sub("x+", "00", date).lstrip("~").split()[0]
            year = int(year.split("-")[0].strip("."))
        except Exception:
            log.print_log(date, "is not a valid date")
            year = "nan"
        ddate = {"when": f"{year}"}
        if date.startswith("~"):
            ddate = {"notBefore": f"{year - 20}", "notAfter": f"{year + 20}"}
        elif date.endswith("Jh."):
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
                factor = 100 / int(second)
                ddate = {"notBefore": year - factor, "notAfter": year - factor + 50}
            else:
                factor = int(second.split("/")[0]) * 100 / int(second.split("/")[1])
                ddate = {
                    "notBefore": year + factor - 25,
                    "notAfter": year + factor,
                }
        tree = ET.Element("date")
        tree.text = date
        for time in ddate:
            tree.attrib[time] = str(ddate[time])
        return tree

    def parse_summary(self, summary, attributes):
        tree = ET.Element("msContents")
        tree.attrib["class"] = attributes
        tree.append(self.title_seek(summary))
        return tree

    @staticmethod
    def title_seek(summary):
        # STUB
        # It still has to identify italics in the Excel table... somehow
        summary = ET.Element("summary")
        return summary

    @staticmethod
    def parse_extension(umfang):
        tree = ET.Element("extent")
        unit = ET.SubElement(tree, "unit")
        unit.attrib["type"] = "leaves"
        unit.attrib["quantity"] = str(umfang)
        return tree

    @staticmethod
    def parse_format(size):
        size = size.replace("*", "x").split("x")
        if len(size) < 2:
            if size:
                size.append(size[0])
            else:
                size = ["", ""]
        tree = ET.Element("support")
        dim = ET.SubElement(tree, "dimensions")
        dim.attrib["unit"] = "mm"
        ET.SubElement(dim, "height").text = size[0]
        ET.SubElement(dim, "width").text = size[1]
        return tree

    @staticmethod
    def parse_signature(signature):
        tree = ET.Element("idno")
        tree.text = signature
        tree.attrib["type"] = "shelfmark"
        return tree

    @staticmethod
    def parse_notation(placeholder):
        # We don't have the source yet.
        tree = ET.Element("musicNotation")
        ET.SubElement(tree, "binaryObject")
        return tree


class TeiStub:
    dictionary = {
        "mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods/mods:titleInfo/mods:title": "teiHeader/fileDesc/titleStmt/title",
        "mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods/mods:originInfo/mods:edition": "teiHeader/fileDesc/editionStmt/p",
        "mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods/mods:physicalDescription/mods:digitalOrigin": "teiHeader/fileDesc/publicationStmt/p",
        "mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods/mods:originInfo/mods:place/mods:placeTerm[@type='text']": "teiHeader/fileDesc/publicationStmt/pubPlace",
        "mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods/mods:originInfo/mods:publisher": "teiHeader/fileDesc/publicationStmt/publisher",
        "mets:amdSec[@ID='AMD']/mets:rightsMD[@ID='RIGHTS']/mets:mdWrap/mets:xmlData/dv:rights/dv:owner": "teiHeader/fileDesc/publicationStmt/authority",
        "mets:amdSec[@ID='AMD']/mets:rightsMD[@ID='RIGHTS']/mets:mdWrap/mets:xmlData/dv:rights/dv:ownerSiteURL": "teiHeader/fileDesc/publicationStmt/address/addrLine",
        "mets:amdSec[@ID='AMD']/mets:rightsMD[@ID='RIGHTS']/mets:mdWrap/mets:xmlData/dv:rights/dv:ownerContact": "teiHeader/fileDesc/publicationStmt/address/email",
        "mets:amdSec[@ID='AMD']/mets:rightsMD[@ID='RIGHTS']/mets:mdWrap/mets:xmlData/dv:rights/dv:sponsor": "teiHeader/fileDesc/publicationStmt/address/sponsor",
        "mets:amdSec[@ID='AMD']/mets:rightsMD[@ID='RIGHTS']/mets:mdWrap/mets:xmlData/dv:rights/dv:license": "teiHeader/fileDesc/publicationStmt/availability/licence",
    }

    def __init__(self, input_tei):
        self.doc_id = os.path.basename(input_tei).rstrip(".xml")
        self.mets = self.get_xml()
        self.tei = self.mets2tei(input_tei, self.mets)

    def get_xml(self):
        mets_doc = False
        url = f"https://viewer.acdh.oeaw.ac.at/viewer/sourcefile?id={self.doc_id}"
        print(url)
        try:
            mets_doc = TeiReader(url)
        except Exception:
            log.print_log(f"{self.doc_id}: {url}", "Problem parsing URL.")
        return mets_doc

    def mets2tei(self, tei_file, mets_tree):
        tei_tree = TeiReader(tei_file)
        for mets_element in self.dictionary:
            self.add_nodes(
                tei_tree.tree.getroot(),
                self.dictionary[mets_element].split("/"),
                mets_tree.tree.xpath(f"//{mets_element}", namespaces=nsmap)[0].text,
            )
        return tei_tree

    @staticmethod
    def parse_attributes(element, value):
        element.text = value
        return element

    def add_nodes(self, tree, nodes, value):
        new_node = self.parse_attributes(
            ET.Element("{http://www.tei-c.org/ns/1.0}" + nodes[0]), ""
        )
        if len(nodes) > 1:
            if parent := tree.xpath(f"//tei:{nodes[0]}", namespaces=nsmap):
                parent = parent[0]
            else:
                tree.append(new_node)
                parent = tree.xpath(f"//tei:{nodes[0]}", namespaces=nsmap)[0]
            self.add_nodes(parent, nodes[1:], value)
        else:
            new_node = self.parse_attributes(new_node, value)
            tree.append(new_node)
        return tree


class TeiTree(TeiStub):
    def __init__(self, input_tei, input_table):
        super().__init__(input_tei)
        self.metadata = Table(input_table).elements[self.doc_id]
        self.table = input_table
        self.header = self.tei.any_xpath("//tei:teiHeader")[0]
        self.sourcedesc = self.header.xpath("//tei:sourceDesc", namespaces=nsmap)[0]
        self.sourcedesc.append(self.make_msdesc(self.metadata))
        self.header.append(self.define_encoding_skeleton())

    @staticmethod
    def make_msdesc(elements):
        tree = ET.Element("msDesc")
        msid = ET.SubElement(tree, "msIdentifier")
        msid.append(elements["Signature"])
        msid.append(elements["Origin"])
        msid.append(elements["Year"])
        tree.append(elements["Summary"])
        physd = ET.SubElement(tree, "physDesc")
        obj = ET.SubElement(physd, "objectDesc")
        obj.attrib["form"] = "codex"
        suppdesc = ET.SubElement(obj, "supportDesc")
        [suppdesc.append(elements[x]) for x in ("Format", "Extension")]
        tree.append(elements["Notation"])
        return tree

    @staticmethod
    def __fill_encoding(desc, attributes):
        root = ET.Element("taxonomy")
        ET.SubElement(root, "desc").text = desc
        for attr in attributes:
            cat = ET.SubElement(root, "category")
            cat.attrib["{http://www.w3.org/XML/1998/namespace}id"] = attr
            ET.SubElement(cat, "catDesc").text = attr[0].upper() + attr[1:]
        return root

    def define_encoding_skeleton(self):
        categories = {
            "Book types": [
                "graduale",
                "antiphonale",
                "sequentiar",
                "psalterium",
                "hymnar",
                "prozessionale",
                "responsoriale",
                "orgelbuch",
                "lamentationen",
                "manuale",
                "litaneien",
                "gesaenge",
                "coralbuch",
                "intonationsbuch",
                "temporale",
            ],
            "Liturgies": ["OFM", "OSC", "OESA"],
        }
        description = "Generiert mit Transkribus, weiterverarbeitet m. custom script"
        tree = ET.Element("encodingDesc")
        ET.SubElement(tree, "p").text = description
        cD = ET.SubElement(tree, "classDecl")
        for taxonomy in categories:
            cD.append(self.__fill_encoding(taxonomy, categories[taxonomy]))
        return tree
