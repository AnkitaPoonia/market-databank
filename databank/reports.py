"""
Market Databank - Professional PDF Report Generation Utility
Powered by ReportLab Platypus Engine
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ----------------------------------------------------------------------
# Font Registration & Unicode Support Setup
# ----------------------------------------------------------------------
PRIMARY_FONT = "Helvetica"
PRIMARY_FONT_BOLD = "Helvetica-Bold"
HAS_UNICODE_FONT = False

# Attempt to register standard Windows Unicode fonts for rupee symbol (₹)
for font_path, font_family in [
    ("C:/Windows/Fonts/segoeui.ttf", "SegoeUI"),
    ("C:/Windows/Fonts/arial.ttf", "ArialCustom"),
    ("C:/Windows/Fonts/calibri.ttf", "CalibriCustom"),
]:
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont(font_family, font_path))
            PRIMARY_FONT = font_family
            PRIMARY_FONT_BOLD = font_family
            HAS_UNICODE_FONT = True
            break
        except Exception:
            pass


def format_currency(amount):
    """
    Format monetary amounts with proper currency symbols and commas.
    Uses '₹' if unicode font registered, otherwise clean 'INR' fallback.
    """
    if amount is None:
        return "N/A"
    try:
        val = float(amount)
        formatted_val = f"{val:,.2f}"
        if HAS_UNICODE_FONT:
            return f"₹ {formatted_val} (INR)"
        return f"INR {formatted_val}"
    except (ValueError, TypeError):
        return str(amount)


# ----------------------------------------------------------------------
# Numbered Canvas for Dynamic Page Numbering ("Page X of Y")
# ----------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    """
    Custom canvas that performs a two-pass save to accurately compute
    the total page count and draw running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.report_date_str = datetime.now().strftime("%B %d, %Y - %H:%M UTC")

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()

        # Top Running Header
        self.setFont(PRIMARY_FONT_BOLD, 7)
        self.setFillColor(colors.HexColor("#14213D"))
        self.drawString(40, letter[1] - 28, "MARKET DATABANK PLATFORM")
        self.setFont(PRIMARY_FONT, 7)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(160, letter[1] - 28, "|  Market Intelligence & Corporate Research Dossier")
        self.drawRightString(letter[0] - 40, letter[1] - 28, "CONFIDENTIAL / RESEARCH ONLY")

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(40, letter[1] - 32, letter[0] - 40, letter[1] - 32)

        # Bottom Running Footer
        self.line(40, 38, letter[0] - 40, 38)
        self.setFont(PRIMARY_FONT, 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(40, 26, f"Report Generated: {self.report_date_str}  |  INT253 Market Databank Project")
        page_label = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 26, page_label)

        self.restoreState()


# ----------------------------------------------------------------------
# PDF Document Builder Function
# ----------------------------------------------------------------------
def generate_dataset_pdf(dataset, buffer):
    """
    Builds a complete, multi-section publication-quality PDF report
    for the given MarketData dataset and writes the binary output to buffer.
    """
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46,
    )

    # Theme Palette Colors
    c_navy = colors.HexColor("#14213D")
    c_blue = colors.HexColor("#2563EB")
    c_slate_bg = colors.HexColor("#F5F7FB")
    c_card_bg = colors.HexColor("#FFFFFF")
    c_muted = colors.HexColor("#64748B")
    c_border = colors.HexColor("#E2E8F0")
    c_text_dark = colors.HexColor("#1E293B")
    c_success = colors.HexColor("#16A34A")
    c_warning = colors.HexColor("#F59E0B")

    # Typography Styles
    styles = getSampleStyleSheet()

    title_banner_style = ParagraphStyle(
        "TitleBanner",
        fontName=PRIMARY_FONT_BOLD,
        fontSize=18,
        leading=22,
        textColor=colors.white,
    )

    subtitle_banner_style = ParagraphStyle(
        "SubBanner",
        fontName=PRIMARY_FONT,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#CBD5E1"),
    )

    section_heading_style = ParagraphStyle(
        "SectionHeading",
        fontName=PRIMARY_FONT_BOLD,
        fontSize=11,
        leading=14,
        textColor=c_navy,
        spaceBefore=10,
        spaceAfter=5,
    )

    cell_label_style = ParagraphStyle(
        "CellLabel",
        fontName=PRIMARY_FONT_BOLD,
        fontSize=8,
        leading=10,
        textColor=c_muted,
    )

    cell_value_style = ParagraphStyle(
        "CellValue",
        fontName=PRIMARY_FONT,
        fontSize=8.5,
        leading=11,
        textColor=c_text_dark,
    )

    metric_title_style = ParagraphStyle(
        "MetricTitle",
        fontName=PRIMARY_FONT,
        fontSize=7.5,
        leading=9,
        textColor=c_muted,
        alignment=1,
    )

    metric_val_style = ParagraphStyle(
        "MetricVal",
        fontName=PRIMARY_FONT_BOLD,
        fontSize=13,
        leading=16,
        textColor=c_navy,
        alignment=1,
    )

    body_desc_style = ParagraphStyle(
        "BodyDesc",
        fontName=PRIMARY_FONT,
        fontSize=8.5,
        leading=13,
        textColor=c_text_dark,
    )

    story = []

    # ------------------------------------------------------------------
    # 1. Header Banner
    # ------------------------------------------------------------------
    header_content = [
        [
            Paragraph("MARKET DATABANK", title_banner_style),
            Paragraph(
                f"<b>Dossier ID:</b> MDB-DATASET-{dataset.pk:05d}<br/>"
                f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}<br/>"
                f"<b>Access Level:</b> {dataset.visibility.upper()}",
                subtitle_banner_style,
            ),
        ],
        [
            Paragraph("Comprehensive Market Research & Corporate Intelligence Dossier", subtitle_banner_style),
            Paragraph(f"<b>Owner:</b> {dataset.created_by.username}", subtitle_banner_style),
        ],
    ]

    header_table = Table(header_content, colWidths=[360, 172])
    header_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), c_navy),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 2. Key Valuation Metrics Block (4 KPI Cards)
    # ------------------------------------------------------------------
    demand_color = c_blue
    if dataset.market_demand == "High":
        demand_color = c_success
    elif dataset.market_demand == "Low":
        demand_color = c_warning

    demand_style = ParagraphStyle(
        "DemandVal",
        fontName=PRIMARY_FONT_BOLD,
        fontSize=12,
        leading=15,
        textColor=demand_color,
        alignment=1,
    )

    growth_text = f"{dataset.market_growth_rate}%" if dataset.market_growth_rate else "N/A"
    size_text = f"${dataset.market_size:,.2f}" if dataset.market_size else "N/A"

    kpi_cards = [
        [
            Paragraph("BENCHMARK MARKET PRICE", metric_title_style),
            Paragraph("MARKET DEMAND LEVEL", metric_title_style),
            Paragraph("EST. TOTAL MARKET SIZE", metric_title_style),
            Paragraph("COMPOUND GROWTH (CAGR)", metric_title_style),
        ],
        [
            Paragraph(format_currency(dataset.market_price), metric_val_style),
            Paragraph(f"{dataset.market_demand} Demand", demand_style),
            Paragraph(size_text, metric_val_style),
            Paragraph(growth_text, metric_val_style),
        ],
    ]

    kpi_table = Table(kpi_cards, colWidths=[133, 133, 133, 133])
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), c_slate_bg),
            ("BOX", (0, 0), (-1, -1), 1, c_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
            ("TOPPADDING", (0, 1), (-1, 1), 2),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # ------------------------------------------------------------------
    # 3. Corporate & Product Specifications
    # ------------------------------------------------------------------
    story.append(Paragraph("1. Corporate & Offering Specifications", section_heading_style))

    spec_data = [
        [
            Paragraph("Dataset Title", cell_label_style),
            Paragraph(dataset.title, cell_value_style),
            Paragraph("Target Entity / Company", cell_label_style),
            Paragraph(dataset.company_name, cell_value_style),
        ],
        [
            Paragraph("Market Sector / Category", cell_label_style),
            Paragraph(dataset.category.name if dataset.category else "General", cell_value_style),
            Paragraph("Industry Niche", cell_label_style),
            Paragraph(dataset.industry, cell_value_style),
        ],
        [
            Paragraph("Product or Offering", cell_label_style),
            Paragraph(dataset.product_service, cell_value_style),
            Paragraph("Visibility Scope", cell_label_style),
            Paragraph(f"<b>{dataset.visibility}</b> Dataset", cell_value_style),
        ],
    ]

    spec_table = Table(spec_data, colWidths=[120, 146, 120, 146])
    spec_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), c_slate_bg),
            ("BACKGROUND", (2, 0), (2, -1), c_slate_bg),
            ("BOX", (0, 0), (-1, -1), 0.8, c_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(spec_table)
    story.append(Spacer(1, 12))

    # ------------------------------------------------------------------
    # 4. Detailed Description & Findings (Automatic Text Wrapping)
    # ------------------------------------------------------------------
    story.append(Paragraph("2. Market Findings & Qualitative Description", section_heading_style))

    desc_content = [[
        Paragraph(
            dataset.description.replace("\n", "<br/>") if dataset.description else "No detailed analysis recorded.",
            body_desc_style,
        )
    ]]

    desc_table = Table(desc_content, colWidths=[532])
    desc_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), c_card_bg),
            ("BOX", (0, 0), (-1, -1), 0.8, c_border),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(desc_table)
    story.append(Spacer(1, 12))

    # ------------------------------------------------------------------
    # 5. Provenance & Audit Metadata
    # ------------------------------------------------------------------
    story.append(Paragraph("3. Research Provenance & Governance", section_heading_style))

    prov_data = [
        [
            Paragraph("Primary Data Source", cell_label_style),
            Paragraph(dataset.data_source, cell_value_style),
            Paragraph("Collection Date", cell_label_style),
            Paragraph(dataset.collection_date.strftime("%B %d, %Y") if dataset.collection_date else "N/A", cell_value_style),
        ],
        [
            Paragraph("Dataset Author / Owner", cell_label_style),
            Paragraph(dataset.created_by.username, cell_value_style),
            Paragraph("Initial Record Date", cell_label_style),
            Paragraph(dataset.created_at.strftime("%Y-%m-%d %H:%M UTC"), cell_value_style),
        ],
        [
            Paragraph("Last Modified Date", cell_label_style),
            Paragraph(dataset.updated_at.strftime("%Y-%m-%d %H:%M UTC"), cell_value_style),
            Paragraph("Governance Status", cell_label_style),
            Paragraph("Verified & Audited Entry", cell_value_style),
        ],
    ]

    prov_table = Table(prov_data, colWidths=[120, 146, 120, 146])
    prov_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), c_slate_bg),
            ("BACKGROUND", (2, 0), (2, -1), c_slate_bg),
            ("BOX", (0, 0), (-1, -1), 0.8, c_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(prov_table)
    story.append(Spacer(1, 14))

    # ------------------------------------------------------------------
    # 6. Disclaimer Notice Box
    # ------------------------------------------------------------------
    notice_text = Paragraph(
        "<b>Notice:</b> This document was dynamically compiled by the Market Databank Generation and Sharing Platform. "
        "All data values and valuation benchmarks reflect user submissions and academic model entries. "
        "Strict Role-Based Access Control governs distribution and replication of this intelligence.",
        ParagraphStyle("Notice", fontName=PRIMARY_FONT, fontSize=7, leading=9, textColor=c_muted),
    )
    notice_table = Table([[notice_text]], colWidths=[532])
    notice_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), c_slate_bg),
            ("BOX", (0, 0), (-1, -1), 0.5, c_border),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(notice_table)

    # Build the document using our custom canvas for dynamic page numbers
    doc.build(story, canvasmaker=NumberedCanvas)

