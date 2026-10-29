import xml.etree.ElementTree as ET
import html

class DrawioFile:
    def __init__(self):
        self.pages = []

    def add_page(self, page_id, name):
        page = DrawioPage(page_id, name)
        self.pages.append(page)
        return page

    def to_xml(self):
        root = ET.Element("mxfile", {
            "host": "app.diagrams.net",
            "modified": "2026-10-28T15:00:00.000Z",
            "agent": "VietJourney UML Studio",
            "version": "22.1.16",
            "type": "device"
        })
        for page in self.pages:
            diag = ET.SubElement(root, "diagram", {"id": page.page_id, "name": page.name})
            model = ET.SubElement(diag, "mxGraphModel", {
                "dx": "1600",
                "dy": "1000",
                "grid": "1",
                "gridSize": "10",
                "guides": "1",
                "tooltips": "1",
                "connect": "1",
                "arrows": "1",
                "fold": "1",
                "page": "1",
                "pageScale": "1",
                "pageWidth": "1654",
                "pageHeight": "1169",
                "math": "0",
                "shadow": "0"
            })
            root_cell = ET.SubElement(model, "root")
            ET.SubElement(root_cell, "mxCell", {"id": "0"})
            ET.SubElement(root_cell, "mxCell", {"id": "1", "parent": "0"})
            for cell in page.cells:
                attrs = {"id": str(cell["id"]), "parent": str(cell["parent"])}
                if cell.get("value") is not None:
                    attrs["value"] = cell["value"]
                if cell.get("style"):
                    attrs["style"] = cell["style"]
                if cell.get("vertex"):
                    attrs["vertex"] = "1"
                if cell.get("edge"):
                    attrs["edge"] = "1"
                if cell.get("source"):
                    attrs["source"] = str(cell["source"])
                if cell.get("target"):
                    attrs["target"] = str(cell["target"])
                
                c_elem = ET.SubElement(root_cell, "mxCell", attrs)
                if cell.get("vertex"):
                    geo = ET.SubElement(c_elem, "mxGeometry", {
                        "x": str(cell["x"]),
                        "y": str(cell["y"]),
                        "width": str(cell["w"]),
                        "height": str(cell["h"]),
                        "as": "geometry"
                    })
                elif cell.get("edge"):
                    geo = ET.SubElement(c_elem, "mxGeometry", {"relative": "1", "as": "geometry"})
                    if cell.get("points"):
                        pts = ET.SubElement(geo, "Array", {"as": "points"})
                        for pt in cell["points"]:
                            ET.SubElement(pts, "mxPoint", {"x": str(pt[0]), "y": str(pt[1])})
        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

class DrawioPage:
    def __init__(self, page_id, name):
        self.page_id = page_id
        self.name = name
        self.cells = []
        self._next_id = 100

    def gen_id(self):
        self._next_id += 1
        return f"{self.page_id}_{self._next_id}"

    def add_vertex(self, cell_id, value, style, x, y, w, h, parent="1"):
        self.cells.append({
            "id": cell_id,
            "value": value,
            "style": style,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "vertex": True,
            "parent": parent
        })
        return cell_id

    def add_edge(self, cell_id, value, style, source, target, points=None, parent="1"):
        self.cells.append({
            "id": cell_id,
            "value": value,
            "style": style,
            "source": source,
            "target": target,
            "points": points,
            "edge": True,
            "parent": parent
        })
        return cell_id
