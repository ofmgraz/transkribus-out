#!/usr/bin/env python3
import glob
from datetime import datetime
from acdh_tei_pyutils.tei import TeiReader
from lxml import etree as ET
import json
import os
import re
import pandas as pd


source_directory = "testdir"
log_file_name = "fetchteiheader"
source_table = "../../goobi-processing/001_src/Quellen_OFM_Graz.xlsx"


with open("mets2tei.json", "r") as f:
    dictionary = json.load(f)

nsmap = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "mets": "http://www.loc.gov/METS/",
    "mods": "http://www.loc.gov/mods/v3",
    "dv": "http://dfg-viewer.de/",
}


def log(log_name, file_name, arg="could not be parsed"):
    now = datetime.now()
    with open(f"{log_name}.log", "a") as f:
        f.write(f'{now.strftime("%Y/%m/%d %H:%M:%S")}\t' f"File `{file_name}` {arg}\n")


def get_xml(docid):
    mets_doc = False
    url = f"https://viewer.acdh.oeaw.ac.at/viewer/sourcefile?id={docid}"
    try:
        mets_doc = TeiReader(url)
    except Exception:
        log(log_file_name, url)
    return mets_doc


def parse_attributes(element, value):
    # if "date" in element.tag:
    #    attr = normalise_date(value)
    #    for x in attr:
    #        element.attrib[x] = attr[x]
    # elifs to do something with the attribs
    # e.g. mods:recordIdentifier[@source='obv-ac']" may be something like'type'?
    element.text = value
    return element


def mets2tei(tei_file, mets_tree):
    tei_tree = TeiReader(tei_file)
    for mets_element in dictionary:
        add_nodes(
            tei_tree.tree,
            dictionary[mets_element].split("/"),
            mets_tree.tree.xpath(f"//{mets_element}", namespaces=nsmap)[0].text,
        )
    return tei_tree


def define_encoding_skeleton():
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
    enc = ET.Element("{http://www.tei-c.org/ns/1.0}encodingDesc")
    ET.SubElement(
        enc, "p"
    ).text = "Generiert mit Transkribus, weiterverarbeitet m. custom script"
    cD = ET.SubElement(enc, "classDecl")
    for taxonomy in categories:
        cD.append(fill_encoding(taxonomy, categories[taxonomy]))
    return enc


def extract_from_table(table):
    elements = {}
    df = pd.read_excel(table)
    df.fillna("", inplace=True)  # Fill empty cells with 0-length strings
    for idx, row in df.iterrows():
        name = row["Signatur"].replace("/", "_").replace(" ", "")
        elements[name] = {}
        elements[name]["Signature"] = parse_signature(row["Signatur"])
        book = classify_books(row["Buchtyp"])
        if row["Liturgie"] == row["Liturgie"]:  # In case of empty cell
            liturgy = f'#{row["Liturgie"].lower()}'
        else:
            liturgy = ""
        elements[name]["Origin"] = parse_origin(row["Provenienz"])
        elements[name]["Year"] = parse_date(str(row["Zeit"]))
        if row["Inhalt"] == row["Inhalt"]:  # In case of empty cell
            content = row["Inhalt"]
        else:
            content = ""
        elements[name]["Summary"] = parse_summary(content, " ".join([book, liturgy]))
        elements[name]["Extension"] = parse_extension(row["Umfang fol."])
        elements[name]["Format"] = parse_format(row["Format"])
        elements[name]["Device"] = row["Gerät"]
        elements[name]["Pictures"] = row["Bilder"]
        elements[name]["Notation"] = parse_notation(False)  # Placeholder
    return elements


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


def parse_origin(origin):
    # it's probably the place of production rather than the archive. It must go somewhere else...
    tree = ET.Element("repository")
    tree.text = origin
    return tree


def parse_date(date):
    try:
        year = re.sub("x+", "00", date).lstrip("~").split()[0]
        year = int(year.split("-")[0].strip("."))
    except Exception:
        log(log_file_name, date, "is not a valid date")
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


def parse_summary(summary, attributes):
    tree = ET.Element("msContents")
    tree.attrib["class"] = attributes
    tree.append(title_seek(summary))
    return tree


def title_seek(summary):
    # STUB
    # It still has to identify italics in the Excel table... somehow
    summary = ET.Element("summary")
    return summary


def parse_extension(umfang):
    tree = ET.Element("extent")
    unit = ET.SubElement(tree, "unit")
    unit.attrib["type"] = "leaves"
    unit.attrib["quantity"] = str(umfang)
    return tree


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


def parse_signature(signature):
    tree = ET.Element("idno")
    tree.text = signature
    tree.attrib["type"] = "shelfmark"
    return tree


def parse_notation(placeholder):
    # We don't have the source yet.
    tree = ET.Element("musicNotation")
    ET.SubElement(tree, "binaryObject")
    return tree


def fill_encoding(desc, attributes):
    root = ET.Element("taxonomy")
    ET.SubElement(root, "desc").text = desc
    for attr in attributes:
        cat = ET.SubElement(root, "category")
        cat.attrib["{http://www.w3.org/XML/1998/namespace}id"] = attr
        ET.SubElement(cat, "catDesc").text = attr[0].upper() + attr[1:]
    return root


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


def add_nodes(tei_tree, nodes, value):
    new_node = parse_attributes(
        ET.Element("{http://www.tei-c.org/ns/1.0}" + nodes[0]), ""
    )
    if len(nodes) > 1:
        if parent := tei_tree.xpath(f"//tei:{nodes[0]}", namespaces=nsmap):
            parent = parent[0]
        else:
            tei_tree.append(new_node)
            parent = tei_tree.xpath(f"//tei:{nodes[0]}", namespaces=nsmap)[0]
        add_nodes(parent, nodes[1:], value)
    else:
        new_node = parse_attributes(new_node, value)
        tei_tree.append(new_node)
    return tei_tree


metadata = extract_from_table(source_table)

for input_file in glob.glob(os.path.join(source_directory, "*.xml")):
    log(log_file_name, input_file, "Parsing")
    docid = os.path.basename(input_file).rstrip(".xml")
    if mets_doc := get_xml(docid):
        tei_doc = mets2tei(input_file, mets_doc)
        header = tei_doc.any_xpath("//tei:teiHeader")[0]
        header.append(define_encoding_skeleton())
        sourcedesc = header.xpath("//tei:sourceDesc", namespaces=nsmap)[0]
        sourcedesc.append(make_msdesc(metadata[docid]))
        with open(f'{input_file.rstrip(".xml")}_m2t.xml', "w") as f:
            f.write(ET.tostring(tei_doc.tree, pretty_print=True, encoding="unicode"))

        # tei_doc.tree_to_file(f'{input_file.rstrip(".xml")}_m2t.xml')
