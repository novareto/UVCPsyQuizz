import uvclight
from cStringIO import StringIO
from zope.interface import Interface
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from tempfile import NamedTemporaryFile
from binascii import a2b_base64

styles = getSampleStyleSheet()


def read_data_uri(uri):
    ctype, data = uri.split(',', 1)
    binary_data = a2b_base64(data)
    fd = StringIO()
    fd.write(binary_data)
    fd.seek(0)
    return fd


class GeneratePDF(uvclight.Page):
    uvclight.context(Interface)
    uvclight.name('pdf')
    uvclight.auth.require('zope.Public')

    def make_response(self, result):
        response = self.responseFactory(app_iter=result)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename="charts.pdf"'
        return response

    def render(self):
        doc = SimpleDocTemplate(NamedTemporaryFile(), pagesize=letter)
        parts = []

        chart = read_data_uri(self.request.form['chart'])
        userschart = read_data_uri(self.request.form['userschart'])

        parts.append(Paragraph(u'Auswertungsbericht', styles['Normal']))
        parts.append(Image(userschart, width=350, height=350))

        image = Image(chart, width=500, height=500,kind='proportional')
        parts.append(image)

        doc.build(parts)
        pdf = doc.filename
        pdf.seek(0)
        return pdf.read()
