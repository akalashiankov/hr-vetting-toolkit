from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

class AuditPDFReport:
    def __init__(self, filename: str):
        self.filename = filename
        self.styles = getSampleStyleSheet()

    def build_report(self, candidate_info: dict, audit_results: list):
        doc = SimpleDocTemplate(
            self.filename, 
            pagesize=letter, 
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )
        story = []

        title_style = ParagraphStyle(
            'Header', parent=self.styles['Heading1'], 
            fontSize=20, textColor=colors.HexColor('#1E293B'), spaceAfter=10
        )
        story.append(Paragraph("Candidate Security Vetting Dossier", title_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

        meta_data = [
            [Paragraph("<b>Full Name:</b>", self.styles['Normal']), Paragraph(candidate_info.get("full_name"), self.styles['Normal'])],
            [Paragraph("<b>Email:</b>", self.styles['Normal']), Paragraph(candidate_info.get("email"), self.styles['Normal'])],
            [Paragraph("<b>Phone:</b>", self.styles['Normal']), Paragraph(candidate_info.get("phone"), self.styles['Normal'])],
            [Paragraph("<b>Consent Timestamp:</b>", self.styles['Normal']), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"), self.styles['Normal'])],
        ]
        meta_table = Table(meta_data, colWidths=[130, 400])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 20))

        story.append(Paragraph("<b>Social Media Audit Findings</b>", self.styles['Heading2']))
        story.append(Spacer(1, 10))

        table_data = [["Platform", "Handle", "Risk Level", "Flagged Content Snippet"]]
        for item in audit_results:
            status_color = "#EF4444" if item["risk_score"] > 0 else "#10B981"
            risk_label = f"<font color='{status_color}'><b>{'FLAGGED' if item['risk_score'] > 0 else 'CLEAR'}</b></font>"
            
            snippets = "<br/>".join([f"• {p['content']}" for p in item["flagged_posts"]]) if item["flagged_posts"] else "No policy risk indicators found."
            
            table_data.append([
                item["platform"], 
                item["handle"], 
                Paragraph(risk_label, self.styles['Normal']), 
                Paragraph(snippets, self.styles['Normal'])
            ])

        findings_table = Table(table_data, colWidths=[80, 100, 80, 270])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(findings_table)

        story.append(Spacer(1, 25))
        disclaimer_text = (
            "<i>Disclaimer: This automated audit report compiles findings strictly from user-consented, publicly available handles. "
            "Flagged indicators do not constitute an automated hiring refusal and must be manually evaluated by HR personnel.</i>"
        )
        story.append(Paragraph(disclaimer_text, self.styles['Italic']))

        doc.build(story)
