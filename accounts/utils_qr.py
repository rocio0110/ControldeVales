import qrcode
from io import BytesIO

def generar_qr_png(data):
    img = qrcode.make(data)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
