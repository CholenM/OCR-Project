import io

import pytest

from modules import document_converter as dc


def test_txt_conversion():
    result = dc.convert_to_markdown("note.txt", b"Hello document")

    assert result.markdown == "Hello document"
    assert result.source_ext == ".txt"
    assert result.strategy == "plain-text"


def test_csv_conversion_to_markdown_table():
    result = dc.convert_to_markdown("sheet.csv", b"name,amount\nAlice,10\nBob,20\n")

    assert result.strategy == "csv"
    assert "| name | amount |" in result.markdown
    assert "| Alice | 10 |" in result.markdown


def test_docx_conversion():
    docx = pytest.importorskip("docx")

    buf = io.BytesIO()
    doc = docx.Document()
    doc.add_heading("Contract", level=1)
    doc.add_paragraph("Payment is due in 30 days.")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Term"
    table.cell(0, 1).text = "Value"
    table.cell(1, 0).text = "Due"
    table.cell(1, 1).text = "30 days"
    doc.save(buf)

    result = dc.convert_to_markdown("contract.docx", buf.getvalue())

    assert result.strategy == "python-docx"
    assert "# Contract" in result.markdown
    assert "| Term | Value |" in result.markdown


def test_unsupported_extension():
    with pytest.raises(dc.ConversionError) as exc:
        dc.convert_to_markdown("archive.zip", b"data")

    assert exc.value.status_code == 400


def test_empty_text_is_unusable():
    with pytest.raises(dc.ConversionError) as exc:
        dc.convert_to_markdown("blank.txt", b"   \n")

    assert exc.value.status_code == 422


def test_libreoffice_missing_reports_actionable_error(monkeypatch):
    monkeypatch.setattr(dc.shutil, "which", lambda _: None)

    with pytest.raises(dc.ConversionError) as exc:
        dc.convert_to_markdown("legacy.doc", b"not really a doc")

    assert exc.value.status_code == 422
    assert "LibreOffice" in str(exc.value)
