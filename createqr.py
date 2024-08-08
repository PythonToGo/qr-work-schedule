import qrcode
import os

# url for QR code
url = 'http://127.0.0.1:8000?show_update=false'

# create QR code
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(url)
qr.make(fit=True)

# save
img = qr.make_image(fill='black', back_color='white')

output_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_dir, 'qrcode.png')

img.save(output_file)