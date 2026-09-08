"""Extracción de texto de los formatos admitidos.

Es el primer paso del flujo documental: sin texto plano no hay clasificación,
resumen, extracción ni búsqueda. Cada familia de formatos tiene su estrategia y
todas devuelven texto normalizado.

| Familia | Extensiones | Estrategia |
|---|---|---|
| Documentos PDF | `.pdf` | `pypdf`; si no hay capa de texto, se envía a la IA para OCR. |
| Word moderno | `.docx` | `python-docx` (párrafos y tablas). |
| Word antiguo | `.doc` | Extracción del texto legible del binario OLE (mejor esfuerzo). |
| OpenDocument | `.odt` | Lectura del `content.xml` del contenedor ZIP. |
| Hojas de cálculo | `.xlsx`, `.xlsm` | Lectura del XML del contenedor: cadenas compartidas y celdas. |
| Presentaciones | `.pptx` | Texto de cada diapositiva. |
| Texto y marcado | `.txt`, `.md`, `.csv`, `.tsv`, `.json`, `.xml`, `.log`, `.ini`, `.yaml`, `.yml`, `.rtf`, `.html`, `.htm` | Lectura directa, con limpieza de etiquetas o de códigos RTF. |
| Imágenes | `.png`, `.jpg`, `.jpeg`, `.webp` | No hay extracción local: las transcribe la IA (OCR). |

Salvo los formatos ZIP de Office, ninguna extracción añade dependencias nuevas.
"""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from docx import Document as DocumentoWord
from pypdf import PdfReader

FORMATOS_TEXTO = {
    ".txt", ".md", ".csv", ".tsv", ".json", ".xml", ".log", ".ini", ".yaml", ".yml",
}
FORMATOS_MARCADO = {".html", ".htm", ".rtf"}
FORMATOS_OFFICE = {".docx", ".doc", ".odt", ".xlsx", ".xlsm", ".pptx"}
FORMATOS_IMAGEN = {".png", ".jpg", ".jpeg", ".webp"}

# Conjunto que la aplicación acepta en la carga.
FORMATOS = {".pdf"} | FORMATOS_TEXTO | FORMATOS_MARCADO | FORMATOS_OFFICE | FORMATOS_IMAGEN

# Longitud mínima para considerar que la extracción sirvió de algo.
MINIMO_UTIL = 20


class ErrorExtraccion(RuntimeError):
    """El archivo existe pero no se pudo convertir a texto localmente."""


def formato_admitido(nombre: str) -> bool:
    return Path(nombre).suffix.lower() in FORMATOS


def normalizar(texto: str) -> str:
    """Colapsa espacios y líneas en blanco repetidas."""
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


# ---------------------------------------------------------------------------
# Estrategias por formato
# ---------------------------------------------------------------------------


def _de_pdf(ruta: Path) -> str:
    lector = PdfReader(str(ruta))
    if lector.is_encrypted:
        raise ErrorExtraccion("El PDF está protegido con contraseña.")
    return "\n".join(pagina.extract_text() or "" for pagina in lector.pages)


def _de_docx(ruta: Path) -> str:
    documento = DocumentoWord(str(ruta))
    partes = [parrafo.text for parrafo in documento.paragraphs]
    for tabla in documento.tables:
        for fila in tabla.rows:
            partes.append(" | ".join(celda.text for celda in fila.cells))
    return "\n".join(partes)


def _de_doc(ruta: Path) -> str:
    """Word 97-2003. Se recupera el texto legible del binario OLE.

    Muchos archivos con extensión `.doc` son en realidad `.docx` renombrados;
    ese caso se detecta por la firma ZIP y se procesa como documento moderno.
    """
    datos = ruta.read_bytes()
    if datos[:2] == b"PK":
        return _de_docx(ruta)
    return _texto_legible(datos)


def _texto_legible(datos: bytes) -> str:
    """Rescata las secuencias de texto de un archivo binario.

    Es una aproximación: prueba las dos codificaciones que usa Word y conserva
    los tramos que parecen lenguaje natural, descartando el ruido binario.
    """
    mejor = ""
    for codificacion in ("utf-16-le", "cp1252"):
        bruto = datos.decode(codificacion, errors="ignore")
        tramos = re.findall(r"[ -~\u00a1-\u017f\n\t]{6,}", bruto)
        utiles = [t.strip() for t in tramos if _parece_texto(t)]
        candidato = "\n".join(utiles)
        if len(candidato) > len(mejor):
            mejor = candidato
    return mejor


def _parece_texto(tramo: str) -> bool:
    """Descarta los tramos con demasiados símbolos, típicos del binario."""
    letras = sum(1 for c in tramo if c.isalpha() or c.isspace())
    return letras >= len(tramo) * 0.7


def _de_txt(ruta: Path) -> str:
    for codificacion in ("utf-8", "utf-16", "latin-1"):
        try:
            return ruta.read_text(encoding=codificacion)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ErrorExtraccion("No se pudo decodificar el archivo de texto.")


def _de_html(ruta: Path) -> str:
    bruto = _de_txt(ruta)
    bruto = re.sub(r"(?is)<(script|style).*?</\1>", " ", bruto)
    bruto = re.sub(r"(?s)<[^>]+>", " ", bruto)
    return html.unescape(bruto)


def _de_rtf(ruta: Path) -> str:
    bruto = _de_txt(ruta)
    bruto = re.sub(r"\\'([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), bruto)
    bruto = re.sub(r"\\par[d]?", "\n", bruto)
    bruto = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", bruto)
    return bruto.replace("{", " ").replace("}", " ")


def _textos_xml(contenido: bytes, sufijo: str) -> list[str]:
    """Devuelve el texto de todas las etiquetas cuyo nombre termine en `sufijo`."""
    raiz = ET.fromstring(contenido)
    return [
        nodo.text
        for nodo in raiz.iter()
        if nodo.tag.endswith(sufijo) and nodo.text and nodo.text.strip()
    ]


def _de_odt(ruta: Path) -> str:
    with zipfile.ZipFile(ruta) as contenedor:
        if "content.xml" not in contenedor.namelist():
            raise ErrorExtraccion("El archivo ODT no contiene `content.xml`.")
        return "\n".join(_textos_xml(contenedor.read("content.xml"), "}p"))


def _de_pptx(ruta: Path) -> str:
    with zipfile.ZipFile(ruta) as contenedor:
        diapositivas = sorted(
            nombre
            for nombre in contenedor.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", nombre)
        )
        partes = []
        for numero, nombre in enumerate(diapositivas, start=1):
            textos = _textos_xml(contenedor.read(nombre), "}t")
            if textos:
                partes.append(f"[Diapositiva {numero}]\n" + "\n".join(textos))
        return "\n\n".join(partes)


def _de_xlsx(ruta: Path) -> str:
    with zipfile.ZipFile(ruta) as contenedor:
        nombres = contenedor.namelist()
        compartidas: list[str] = []
        if "xl/sharedStrings.xml" in nombres:
            raiz = ET.fromstring(contenedor.read("xl/sharedStrings.xml"))
            for entrada in raiz:
                compartidas.append(
                    "".join(
                        nodo.text or ""
                        for nodo in entrada.iter()
                        if nodo.tag.endswith("}t")
                    )
                )

        lineas = []
        hojas = sorted(n for n in nombres if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n))
        for numero, hoja in enumerate(hojas, start=1):
            raiz = ET.fromstring(contenedor.read(hoja))
            filas_hoja = []
            for fila in raiz.iter():
                if not fila.tag.endswith("}row"):
                    continue
                celdas = []
                for celda in fila:
                    valor = _valor_de_celda(celda, compartidas)
                    if valor:
                        celdas.append(valor)
                if celdas:
                    filas_hoja.append(" | ".join(celdas))
            if filas_hoja:
                lineas.append(f"[Hoja {numero}]")
                lineas.extend(filas_hoja)
        return "\n".join(lineas)


def _valor_de_celda(celda, compartidas: list[str]) -> str:
    """Resuelve el contenido de una celda, sea literal o cadena compartida."""
    tipo = celda.get("t")
    for hijo in celda:
        if hijo.tag.endswith("}is"):
            return "".join(
                nodo.text or "" for nodo in hijo.iter() if nodo.tag.endswith("}t")
            )
        if hijo.tag.endswith("}v"):
            valor = hijo.text or ""
            if tipo == "s":
                try:
                    return compartidas[int(valor)]
                except (ValueError, IndexError):
                    return valor
            return valor
    return ""


ESTRATEGIAS = {
    ".pdf": _de_pdf,
    ".docx": _de_docx,
    ".doc": _de_doc,
    ".odt": _de_odt,
    ".pptx": _de_pptx,
    ".xlsx": _de_xlsx,
    ".xlsm": _de_xlsx,
    ".rtf": _de_rtf,
    ".html": _de_html,
    ".htm": _de_html,
}


def extraer_texto(ruta: str | Path) -> str:
    """Devuelve el texto plano de un archivo admitido.

    Lanza ``ErrorExtraccion`` si el formato no se admite, el archivo no existe o
    el contenido no es legible localmente. En ese último caso la capa de
    procesamiento puede intentar la transcripción con IA.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorExtraccion("El archivo físico no existe en el almacenamiento.")

    extension = ruta.suffix.lower()
    if extension not in FORMATOS:
        raise ErrorExtraccion(f"Formato no admitido: {extension or 'sin extensión'}.")
    if extension in FORMATOS_IMAGEN:
        raise ErrorExtraccion("Las imágenes se transcriben con IA, no localmente.")

    estrategia = ESTRATEGIAS.get(extension, _de_txt)
    try:
        texto = estrategia(ruta)
    except ErrorExtraccion:
        raise
    except Exception as exc:  # librerías de terceros con errores heterogéneos
        raise ErrorExtraccion(f"No se pudo leer el archivo: {exc}") from exc

    texto = normalizar(texto)
    if len(texto) < MINIMO_UTIL:
        raise ErrorExtraccion(
            "El archivo no contiene texto legible (puede ser un documento escaneado)."
        )
    return texto


def dividir_en_fragmentos(texto: str, tamano: int = 1200, solape: int = 150) -> list[str]:
    """Parte el texto en fragmentos con solape para indexarlos por separado.

    El solape evita que una frase quede cortada entre dos fragmentos y se
    pierda en la búsqueda semántica.
    """
    texto = (texto or "").strip()
    if not texto:
        return []
    if len(texto) <= tamano:
        return [texto]

    fragmentos: list[str] = []
    inicio = 0
    while inicio < len(texto):
        fin = inicio + tamano
        fragmento = texto[inicio:fin]
        # Cierra el fragmento en el último punto o salto de línea disponible.
        if fin < len(texto):
            corte = max(fragmento.rfind(". "), fragmento.rfind("\n"))
            if corte > tamano // 2:
                fragmento = fragmento[: corte + 1]
                fin = inicio + corte + 1
        fragmentos.append(fragmento.strip())
        siguiente = fin - solape
        inicio = siguiente if siguiente > inicio else fin
    return [f for f in fragmentos if f]
