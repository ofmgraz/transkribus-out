from datetime import datetime
from acdh_tei_pyutils.tei import TeiReader, ET
import json
import os
import re
import pandas as pd
import requests

# https://loris.acdh.oeaw.ac.at/uuid:/ofmgraz/derivatives/\{A67_21\}/\{A-Gf_A67_21-001r\}.tif/full/full/0/default.jpg
nsmap = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "mets": "http://www.loc.gov/METS/",
    "mods": "http://www.loc.gov/mods/v3",
    "dv": "http://dfg-viewer.de/",
    "default": "http://www.tei-c.org/ns/1.0",
}

xml = "{http://www.w3.org/XML/1998/namespace}"
tei = "{http://www.tei-c.org/ns/1.0}"

locations = TeiReader("data/indices/listplace.xml")
persons = TeiReader("data/indices/listperson.xml")
persons = TeiReader("data/indices/listperson.xml")

titles_deen = {
    "Antiphonale": "Antiphonal",
    "Choralbuch": "Choir book",
    "Graduale": "Gradual",
    "Hymnar": "Hymnary",
    "Intonationsbuch": "Book of Intonations",
    "Lamentationen": "Lamentations",
    "Lehrbuch": "Textbook",
    "Litaneien": "Litanies",
    "Manuale": "Manuals",
    "Marianische Gesänge": "Marian chants",
    "Orgelbuch": "Organ book",
    "Prozessionale": "Processionale",
    "Psalterium": "Psalterium",
    "Responsoriale": "Responsoriale",
    "Sequentiar": "Book of Sequences",
}


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
    def __init__(self, source_tkb, source_tei):
        self.filename = source_tkb
        self.doc_id = os.path.basename(source_tkb).strip()
        self.tei = self.read_xml_input(source_tei)
        self.root = self.tei.any_xpath("//tei:TEI")[0]
        self.header = self.tei.any_xpath("//tei:teiHeader")[0]

    @staticmethod
    def read_xml_input(input_file):
        try:
            tree = TeiReader(input_file)
            for bad in tree.any_xpath(".//tei:span"):
                bad.getparent().remove(bad)
        except Exception as e:
            log.print_log(input_file, e, True)
            tree = False
        return tree

    @staticmethod
    def make_printable(tree):
        p1 = ET.ProcessingInstruction(
            "xml-model",
            'href="https://id.acdh.oeaw.ac.at/ofmgraz/schema.rng" type="application/xml" '
            'schematypens="http://relaxng.org/ns/structure/1.0"',
        )
        # p2 = ET.ProcessingInstruction("xml-model",
        # 'href="https://id.acdh.oeaw.ac.at/ofmgraz/schema.odd"',
        # type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0")

        # parser = ET.XMLParser(remove_blank_text=True, encoding="utf-8")
        # string = ET.tostring(tree, encoding="utf-8")
        root = tree.getroot()
        # xml = ET.fromstring(string, parser=parser)
        root.addprevious(p1)
        # treer = ET.ElementTree(tree)
        return ET.tostring(root, pretty_print=True, xml_declaration=True)


class TeiBody(TeiTree):
    def __init__(self, source_tkb, source_tei):
        super().__init__(source_tkb, source_tei)
        self.tkb = self.read_xml_input(self.filename)
        self.tkb = self.amend_pics_url(self.tkb, self.doc_id)
        self.root.append(self.tkb.any_xpath("//tei:facsimile")[0])
        self.root.append(self.tkb.any_xpath("//tei:text")[0])
        # self.make_text()
        self.printable = self.make_printable(self.tei.tree)

    def make_text(self):
        # Stub to include later required divs or milestones if required
        body = self.tei.any_xpath(".//tei:body")[0]
        for element in body.xpath(".//tei:div/*", namespaces=nsmap):
            if element.tag == f"{tei}pb":
                page = ET.SubElement(body, "div", attrib={"type": "page"})
                element.attrib["source"] = self.get_graphicid(element.attrib["facs"])
                page.append(element)
                p = ET.SubElement(page, "p", attrib={"facs": element.attrib["facs"]})
            elif element.tag == f"{tei}ab":
                elefake = ET.fromstring(
                    ET.tostring(element, pretty_print=True, encoding="utf-8")
                )
                for t in elefake.xpath(".//*"):
                    p.append(t)
                # for lb in element.iter():
                #    if lb.tag:
                #        line = ET.SubElement(page, "li", attrib=lb.attrib)
                #        line.text = lb.tail
        body.remove(body.xpath("./tei:div", namespaces=nsmap)[0])
        # e.getparent().remove(e)

    @staticmethod
    def amend_pics_url(tree, doc_id):
        graphic_elements = tree.any_xpath(".//tei:graphic")
        for element in graphic_elements:
            img_name = (
                element.attrib["url"].replace("Gu", "Gf").split(".jpg")[0].strip()
            )
            if len(img_name) < 1 or img_name.isdigit():
                element.getparent().remove(element)
            else:
                if "http" in img_name:
                    response = requests.get(element.attrib["url"])
                    img_name = (
                        response.headers.get("Content-Disposition")
                        .split("filename=")[1]
                        .split(".jpg")[0]
                        .strip('"')
                    )
                img_name = img_name.replace("Gu", "Gf").split(".jpg")[0]
                img_name = re.sub(r"^.*A-Gf_", "A-Gf_", img_name)
                img_name = re.sub(r"^[\d_]*", "", img_name)
                img_name = re.sub(r"A-Gf_([\d])", "A-Gf_A\g<1>", img_name)
                img_name = re.sub(r"A-Gf_A_([\d])", "A-Gf_A\g<1>", img_name)
                if tree.any_xpath(".//tei:measure[@unit = 'page']"):
                    img_name = re.sub(r"(A-Gf_S\d_\d*-\d*)[rv]", "\g<1>", img_name)
                if "A63_51" in img_name:
                    new_base_url = "https://iiif.acdh.oeaw.ac.at/iiif/images/ofmgraz"
                    img_name = f"{img_name}.jp2"
                else:
                    new_base_url = "https://viewer.acdh.oeaw.ac.at/viewer/api/v1/records"
                    img_name = f"{doc_id.rstrip('.xml')}/files/images/{img_name}"
                element.attrib["url"] = f"{new_base_url}/{img_name}/full/!1024,1024/0/default.jpg"
                # f"https://loris.acdh.oeaw.ac.at/uuid:/ofmgraz/derivatives/{doc_id.rstrip('.xml')}/{img_name}.tif/full/full/0/default.jpg"
        # e.g. https://viewer.acdh.oeaw.ac.at/viewer/content/A67_17/800/0/A-Gf_A67_17-012v.jpg
        return tree


class TeiHeader(TeiTree):
    def __init__(self, source_tkb, source_tei, source_table):
        super().__init__(source_tkb, source_tei)
        self.tablename = source_table
        # self.add_digitaledition_origin()
        self.make_meta()
        self.msdesc = self.tei.any_xpath("//tei:msDesc")[0]
        self.elements = self.extract_from_table(source_table, self.header)
        self.printable = self.make_printable(self.tei.tree)

    def make_meta(self):
        self.root.attrib[f"{xml}id"] = self.doc_id
        self.root.attrib[f"{xml}base"] = "https://id.acdh.oeaw.ac.at/ofmgraz/teidocs"

    def make_hodie(self):
        hodie = datetime.today().strftime("%Y-%m-%d")
        date = self.header.xpath(
            "//tei:fileDesc/tei:publicationStmt/tei:date", namespaces=nsmap
        )[0]
        date.attrib["when-iso"] = hodie
        date.text = hodie

    @staticmethod
    def read_table(table):
        try:
            df = pd.read_json(table, orient="index").fillna("")
        except Exception as e:
            log.print_log(table, f"WARNING: {e}", True)
            try:
                df = pd.read_excel(table).fillna("")
            except Exception as e:
                log.print_log(table, e, True)
        return df

    def extract_from_table(self, table, header):
        self.header = header
        df = self.read_table(table)
        column_name = (
            self.doc_id[0] + " " + self.doc_id[1:].replace("_", "/").rstrip(".xml")
        )
        for idx, row in df.loc[df["Signatur"] == column_name].iterrows():
            self.make_title(
                row["Titel"], row["Title_en"], row["Inhalt"], row["Incipit"], row["Signatur"]
            )
            self.parse_signature(row["Signatur"])
            self.parse_origin(row["Provenienz"], publisher=row["Drucker"])
            self.parse_date(str(row["Zeit"]))
            booktypes = [booktype['value'] for booktype in row['Buchtyp']]
            if booktypes and row["Liturgie"]:
                keys = self.classify_books(booktypes, row["Liturgie"])
            self.parse_summary(row["Inhalt"], row["Buchtyp"], keys)
            self.parse_extension(row["Umfang fol."])
            self.parse_format(row["Format"])
            self.parse_notation(False)  # Placeholder
            self.parse_photographer(row["Fotograf"], row["Bearbeiter"])
            self.parse_device(row["Gerät"])

    def make_title(self, title, title_en, summary, incipit, signature):
        xmltitle = self.header.xpath("//tei:titleStmt/tei:title[@type='main' and @xml:lang='de']", namespaces=nsmap)[0]
        xmltitle_en = self.header.xpath("//tei:titleStmt/tei:title[@type='main' and @xml:lang='en']", namespaces=nsmap)[0]
        xmldesc = self.header.xpath("//tei:titleStmt/tei:title[@type='desc']", namespaces=nsmap)[0]
        # filedesc = self.header.xpath("//tei:fileDesc", namespaces=nsmap)[0]
        #tistmt = filedesc.xpath("./tei:titleStmt", namespaces=nsmap)[0]
        shelfmark = f"A-Gf {signature}"
        xmltitle.text = title
        xmltitle_en.text = title_en
        print('TITLES', xmltitle, xmltitle_en)
        xmldesc.text = shelfmark
        # ET.SubElement(tistmt, "title", type="sub").text = f"{title} ({shelfmark})"
        # ET.SubElement(filedesc, "sourceDesc").text = f"{title} ({shelfmark})"

    def parse_signature(self, sign):
        # sign = sign.replace("/", "_").replace(" ", "")
        self.msdesc.xpath("//tei:msIdentifier/tei:idno", namespaces=nsmap)[
            0
        ].text = f"A-Gf {sign}"

    @staticmethod
    def make_pid(pid):
        pid = re.sub(r"[\?\s\.]", "", pid)
        pid = pid.replace("ü", "ue").replace("ö", "oe")
        return pid

    def parse_origin(self, origin, publisher=False):
        locations = TeiReader("data/indices/listplace.xml")
        origins = [x.strip() for x in origin.split(",")]
        pid = self.make_pid(origins[0])
        listplace = self.root.xpath(".//tei:standOff/tei:listPlace", namespaces=nsmap)
        #listrelation = self.root.xpath(".//tei:standOff/tei:listRelation", namespaces=nsmap)
        if len(listplace) < 1:
            listplace = ET.SubElement(
                self.root.xpath(".//tei:standOff", namespaces=nsmap)[0], "listPlace"
            )
            #listrelation = ET.SubElement(
            #    self.root.xpath(".//tei:standOff", namespaces=nsmap)[0], "listRelation"
            #    )
        print(f"PID: {pid}")
        if pid and not self.root.xpath(
            f'.//tei:place[@xml:id="{pid}"]', namespaces=nsmap
        ):
            for location in  locations.any_xpath(f'.//tei:place[@xml:id="{pid}"]'):
                # Entry in the standOff list of places
                # place = ET.SubElement(tree, "place")
                listplace.append(
                    ET.fromstring(
                        ET.tostring(location, pretty_print=True, encoding="utf-8")
                    )
                )
            #    listrelation.append(
            #        ET.fromstring(f'<relation type="geographical" name="provenance" passive="{self.filename}" active="#{pid}"/>')
            #    )
        # Element in msDesc/history referencing the entry above
        provenance = self.msdesc.xpath(
            "./tei:history/tei:provenance", namespaces=nsmap
        )[0]
        attribs = {"ref": f"#{pid}"}
        if "?" in origins[0]:
            attribs["cert"] = "medium"
        placename = ET.SubElement(provenance, "placeName", attrib=attribs)
        placename.text = origins[0]
        if publisher:
            self.make_publisher(publisher)
            # self.make_idno(place, dictentry["place"]["idno"])
        if len(origins) > 1:
            self.parse_origin(",".join(origins[1:]), False)
        if len(origins) < 1:
            self.parse_origin(",".join(origins[1:]), False)

    def add_digitaledition_origin(self):
        tree = ET.SubElement(
            self.tei.any_xpath(".//tei:standOff")[0], f"{tei}listPlace"
        )
        entry = ET.fromstring(
            ET.tostring(
                locations.any_xpath('//tei:place[@xml:id="Wien"]')[0],
                pretty_print=True,
                encoding="utf-8",
            )
        )
        tree.append(entry)

    def make_publisher(self, publisher):
        entry = False
        listperson =  ET.SubElement(self.tei.any_xpath(".//tei:standOff")[0], "listPerson")
        #listperson = self.tei.any_xpath(".//tei:standOff/tei:listPerson")
        #listperson = ET.SubElement(self.tei.any_xpath(".//tei:standOff/tei:listPerson")[0], "listPerson")
        #listrelation = ET.SubElement(self.tei.any_xpath(".//tei:standOff/tei:listRelation")[0], "listRelation")
        for person in persons.any_xpath(f'//tei:person[@xml:id="{publisher}"]'):
            entry = ET.fromstring(
                ET.tostring(person, pretty_print=True, encoding="utf-8")
            )
            #relation =  ET.fromstring(f'<relation type="creation" name="printing" passive="{self.filename}" active="#{publisher}"/>')
            listperson.append(entry)
            # listrelation.append(relation)

            break
        if len(entry) > 0:
            place = person.xpath(
                "//tei:residence/tei:settlement/tei:placeName", namespaces=nsmap
            )[0]
            fullname = " ".join(
                [
                    n.strip()
                    for n in entry.xpath("//tei:persName", namespaces=nsmap)[
                        0
                    ].itertext()
                ]
            ).strip()
            fullname = fullname.replace("  ", " ")
            bibl = self.header.xpath(
                "//tei:fileDesc/tei:sourceDesc/tei:bibl", namespaces=nsmap
            )[0]
            ET.SubElement(
                bibl, "pubPlace", attrib={"ref": place.attrib["ref"]}
            ).text = place.text
            ET.SubElement(
                bibl, "publisher", attrib={"ref": f"#{publisher}"}
            ).text = fullname.strip()
            self.msdesc.xpath("//tei:physDesc/tei:objectDesc", namespaces=nsmap)[
                0
            ].attrib["form"] = "print"

            self.header.xpath(
                "//tei:profileDesc/tei:textDesc/tei:channel", namespaces=nsmap
            )[0].text = "book"

    @staticmethod
    def make_idno(person, idno):
        for i in idno:
            ET.SubElement(
                person, "idno", attrib={"type": "URL", "subtype": i}
            ).text = idno[i]

    def parse_date(self, date):
        element = self.msdesc.xpath(
            "//tei:fileDesc/tei:sourceDesc/tei:bibl/tei:date", namespaces=nsmap
        )[0]
        nb = "-01-01"
        na = "-12-31"
        try:
            year = re.sub("x+", "00", date).lstrip("~").split()[0]
            year = int(year.split("-")[0].strip("."))
        except Exception as e:
            log.print_log(self.tablename, e)
            year = "1500"
        if year == 2023:
            ddate = {"notBefore": f"1000{nb}", "notAfter": f"{year}{na}"}
        elif date.startswith("~"):
            ddate = {"notBefore": f"{year - 20}{nb}", "notAfter": f"{year + 20}{na}"}
        elif date.endswith("Jh.") or re.match(r"^\d{2}$", date):
            if "/" in date:
                dates = date.split("/")
                yb = int(re.match(r"\d+", dates[0]).group(0))
                ya = int(re.match(r"\d+", dates[1]).group(0))
                ddate = {
                    "notBefore": f"{yb  * 100}{nb}",
                    "notAfter": f"{ya  * 100}{nb}",
                }
            else:
                ddate = {
                    "notBefore": f"{(year - 1) * 100}{nb}",
                    "notAfter": f"{(year - 1) * 100 + 99}{na}",
                }
        elif date.endswith("x"):
            ddate = {"notBefore": f"{year}{nb}", "notAfter": f"{year + 99}{na}"}
        elif re.findall(r"^\d{2}\-\d(?:/\d)*", date):
            second = date.split("-")[1]
            year *= 100
            if second in "12":
                factor = int(100 / int(second))
                ddate = {
                    "notBefore": f"{year - factor}{nb}",
                    "notAfter": f"{year - factor + 50}{na}",
                }
            else:
                factor = int(
                    int(second.split("/")[0]) * 100 / int(second.split("/")[1])
                )
                ddate = {
                    "notBefore": f"{year + factor - 25}{nb}",
                    "notAfter": f"{year + factor}{na}",
                }
        else:
            ddate = {"notBefore": f"{year}{nb}", "notAfter": f"{year}{na}"}
        element.text = date
        for time in ddate:
            element.attrib[time] = str(ddate[time])

    def classify_books(self, btype, lit):
        classdecl = ET.SubElement(
            self.header.xpath("//tei:encodingDesc", namespaces=nsmap)[0], "classDecl"
        )
        keys = ""
        if lit:
            tax = ET.SubElement(classdecl, "taxonomy", attrib={f"{xml}id": "liturgies"})
            ET.SubElement(tax, "desc").text = "Liturgies"
            keys = f"#{lit.lower()}"
            cat = ET.Element("category", attrib={f"{xml}id": lit.lower()})
            ET.SubElement(cat, "catDesc").text = lit
            tax.append(cat)
        
        if btype:
            tax = ET.SubElement(classdecl, "taxonomy", attrib={f"{xml}id": "booktypes"})
            ET.SubElement(tax, "desc").text = "Book Types"
            for book in btype:
                cat = ET.Element("category", attrib={f"{xml}id": book})
                ET.SubElement(cat, "catDesc").text = book
                keys += f" #{book}"
        return keys

    def parse_summary(self, summary, bookt, attributes):
        if summary != summary:
            summary = ""
        elif not summary.strip().endswith('.') and len(summary) > 0:
            summary = summary.strip() + "." 
        summary = summary.replace("„", "<title>").replace("“", "</title>")
        element = self.msdesc.xpath("//tei:msContents", namespaces=nsmap)[0]
        if attributes:
            element.attrib["class"] = attributes.strip()
        subelement = element.xpath("//tei:summary", namespaces=nsmap)[0]
        if summary:
            subelement.append(ET.fromstring(f"<p>{summary}</p>"))
        subelement.append(ET.fromstring(f"<p>{', '.join([book['value'] for book in bookt])}.</p>"))

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
        if self.msdesc.xpath(
            ".//tei:objectDesc[@form ='print']", namespaces=nsmap
        ) or self.msdesc.xpath(".//tei:idno[@type ='shelfmark']", namespaces=nsmap)[
            0
        ] in (
            "A-Gf S 1/23",
            "A-Gf S 1/25",
            "A-Gf S 1/26",
        ):
            # S1/23 is a exception
            tree.attrib["unit"] = "page"
        else:
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

    def get_graphicid(self, facs):
        facs = facs.strip("#")
        url = self.tei.any_xpath(f'.//tei:surface[@xml:id="{facs}"]/tei:graphic/@url')[
            0
        ]
        return url.replace("full/full", "full/600,")

    def parse_photographer(self, photographer, other=""):
        roles = [
            ["FS", "XML Datenmodellierung", "XML modelling", "MetadataCreator"],
            ["PA", "Datengenerierung", "Data generation", "Contributor"],
            ["DS", "Datengenerierung", "Data Generation", "Contributor"],
            ["RK", "Datengenerierung", "Data generation", "Contributor"],
            [
                photographer,
                "Digitalisierung (Fotografieren) des Archivmaterials",
                "Digitisation (photography) of the archival materials",
                "DigitisingAgent",
            ],
        ]
        if len(other) > 0:
            roles.append([other, "Transkribus Bearbeitung", "Transkribus manipulation", "Transcriptor"])
        titlestmt = self.header.xpath(".//tei:titleStmt", namespaces=nsmap)[0]
        for person in roles:
            resps = TeiReader("data/constants/resp.xml")
            respstmt = ET.SubElement(titlestmt, "respStmt")
            if resps.any_xpath(f'.//tei:person[@xml:id="{person[0]}"]/tei:persName'):
                collaborator = resps.any_xpath(
                    f'.//tei:person[@xml:id="{person[0]}"]/tei:persName'
                )[0]
                collaborator.attrib["role"] = person[3]
                p = ET.SubElement(respstmt, "resp", attrib={f"{xml}lang": "de"})
                p.text = person[1]
                p = ET.SubElement(respstmt, "resp", attrib={f"{xml}lang": "en"})
                p.text = person[2]
                respstmt.append(collaborator)

    def parse_device(self, device):
        devices = {"Stativlaser": "Stativlaser", "Traveller": "Traveller"}
        note = self.header.xpath(
            f'//tei:fileDesc/tei:notesStmt/tei:note[@xml:lang="de"]', namespaces=nsmap
        )[0]
        note.text = f"Originale mit einem {devices[device]}-Gerät digitalisiert"
        note = self.header.xpath(
            f'//tei:fileDesc/tei:notesStmt/tei:note[@xml:lang="en"]', namespaces=nsmap
        )[0]
        note.text = f"Originals digitised with a {devices[device]} device"
