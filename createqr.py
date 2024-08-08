import qrcode
import os

# URL for QR code
url = 'https://qr-work-schedule.vercel.app?show_update=false'  # Vercel에서 제공된 URL로 변경

# Create QR code
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(url)
qr.make(fit=True)

# Save
img = qr.make_image(fill='black', back_color='white')

output_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_dir, 'qrcode.png')

img.save(output_file)

print(f"QR 코드가 생성되었습니다. '{output_file}' 파일을 확인하세요.")
