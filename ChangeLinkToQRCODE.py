import qrcode
import qrcode.constants
import sys
import os
from PIL import Image, ImageDraw, ImageOps, ImageFont, ImageFilter

# ================================
#      ADD LABEL BELOW QR
# ================================

def add_label_below_qr(qr_img, text, font_size=32):
    """Thêm tên/nhãn ở dưới QR (tương thích nhiều phiên bản Pillow)."""
    # Chọn font: ưu tiên arial.ttf nếu có, ngược lại dùng font mặc định
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    w, h = qr_img.size

    # Tính kích thước chữ theo cách tương thích
    try:
        # Pillow mới: trả về (x0, y0, x1, y1)
        bbox = ImageDraw.Draw(qr_img).textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except Exception:
        try:
            # Một số phiên bản có textsize
            text_w, text_h = ImageDraw.Draw(qr_img).textsize(text, font=font)
        except Exception:
            # Fallback: dùng font.getsize (cũ/ổn định)
            try:
                text_w, text_h = font.getsize(text)
            except Exception:
                # Nếu tất cả thất bại, đặt một kích thước mặc định
                text_w, text_h = (len(text) * (font_size // 2), font_size)

    # Tăng chiều cao để chứa dòng chữ (thêm padding)
    padding = 10
    new_h = h + text_h + padding * 2
    new_img = Image.new("RGB", (w, new_h), "white")
    new_img.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(new_img)

    # Vẽ chữ căn giữa (ở vị trí h + padding)
    x = (w - text_w) // 2
    y = h + padding

    draw.text((x, y), text, font=font, fill="black")

    return new_img


# ================================
#       CORE FUNCTIONS
# ================================

def create_qr_object(data, error_correction, fill_color, back_color):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_data_len = len(data)
        
        return qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
    except Exception as e:
        raise Exception(f"Lỗi khi tạo đối tượng QR code: {e}")


def save_qr_image(qr_img, filename, suffix=""):
    try:
        final_filename = f"{filename}{suffix}.png"
        qr_img.save(final_filename)
        print(f"\n✅ Đã tạo mã QR thành công và lưu tại: {final_filename}")
        return True
    except Exception as e:
        print(f"\n❌ Lỗi khi lưu file: {e}")
        return False


# ================================
#       QR FUNCTIONS
# ================================

def create_basic_qr(data, filename, fill_color="black", back_color="white",
                    error_correction=qrcode.constants.ERROR_CORRECT_M):
    try:
        qr_img = create_qr_object(data, error_correction, fill_color, back_color)

        # ⬅️ GẮN LABEL DƯỚI QR
        qr_img = add_label_below_qr(qr_img, filename)

        save_qr_image(qr_img, filename)
    except Exception as e:
        print(f"\n❌ Lỗi tạo QR cơ bản: {e}")


def create_custom_qr():
    print("\n--- Tạo Mã QR Tùy chỉnh ---")

    data = input("Nhập dữ liệu (URL/Text): ")
    filename = input("Nhập tên file để lưu: ")

    fill_color = input("Nhập màu QR (mặc định black): ") or "black"
    back_color = input("Nhập màu nền (mặc định white): ") or "white"

    print("\nChọn mức độ sửa lỗi:")
    print("L = 7% | M = 15% | Q = 25% | H = 30%")
    ec = input("Nhập mức (L/M/Q/H, mặc định M): ").upper() or "M"

    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H
    }

    error_correction = ec_map.get(ec, qrcode.constants.ERROR_CORRECT_M)

    create_basic_qr(data, filename, fill_color, back_color, error_correction)


def create_wifi_qr():
    print("\n--- Tạo Mã QR Wi-Fi ---")
    ssid = input("Nhập tên mạng (SSID): ")
    password = input("Nhập mật khẩu Wi-Fi: ")
    security_type = input("Nhập kiểu bảo mật (WPA/WEP/NONE, mặc định WPA): ").upper() or "WPA"
    is_hidden = input("Mạng ẩn? (y/n, mặc định n): ").lower()

    hidden_param = "true" if is_hidden == 'y' else "false"

    wifi_data = f"WIFI:T:{security_type};S:{ssid};P:{password};H:{hidden_param};;"
    filename = f"wifi_{ssid}"

    create_basic_qr(wifi_data, filename)


def create_vcard_qr():
    print("\n--- Tạo Mã QR Danh thiếp (VCard) ---")

    name = input("Nhập Họ và Tên: ")
    phone = input("Nhập Số điện thoại: ")
    email = input("Nhập Email: ")
    company = input("Nhập Công ty (không bắt buộc): ")
    title = input("Nhập Chức danh (không bắt buộc): ")

    filename = f"vcard_{name.replace(' ', '_')}"

    vcard_lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{name};;;",
        f"FN:{name}",
        f"TEL;TYPE=CELL:{phone}",
        f"EMAIL:{email}",
    ]
    if company:
        vcard_lines.append(f"ORG:{company}")
    if title:
        vcard_lines.append(f"TITLE:{title}")

    vcard_lines.append("END:VCARD")

    vcard_data = "\n".join(vcard_lines)

    create_basic_qr(vcard_data, filename,
                    error_correction=qrcode.constants.ERROR_CORRECT_H)


def create_qr_with_logo():
    print("\n--- Tạo Mã QR Có Logo ---")

    data = input("Nhập dữ liệu (URL/Text): ")
    filename = input("Nhập tên file: ")
    logo_path = input("Nhập tệp logo (logo.png): ")

    fill_color = input("Nhập màu QR (mặc định black): ") or "black"

    if not os.path.exists(logo_path):
        print(f"❌ Không tìm thấy file logo: {logo_path}")
        return

    try:
        from PIL import ImageFilter, ImageFont

        # === TẠO QR ===
        qr_img = create_qr_object(
            data=data,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            fill_color=fill_color,
            back_color="white"
        )

        qr_w, qr_h = qr_img.size  # LẤY KÍCH THƯỚC QR CHÍNH XÁC

        # === TẢI LOGO ===
        logo = Image.open(logo_path).convert("RGBA")

        # Tăng độ sắc nét logo
        upscale = 2
        logo = logo.resize((logo.width * upscale, logo.height * upscale), Image.LANCZOS)
        logo = logo.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

        # === TÍNH TỈ LỆ LOGO THEO ĐỘ DÀI DATA ===
        qr_data_len = len(data)
        if qr_data_len < 50:
            ratio = 0.25
        elif qr_data_len < 150:
            ratio = 0.20
        else:
            ratio = 0.15

        logo_size = int(qr_w * ratio)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        # === TẠO MASK TRÒN ===
        mask = Image.new("L", (logo_size, logo_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, logo_size, logo_size), fill=255)

        logo_round = Image.new("RGBA", (logo_size, logo_size))
        logo_round.paste(logo, (0, 0), mask=mask)

        # === TẠO VIỀN TRẮNG ===
        border_size = 6
        final_logo_size = logo_size + border_size * 2

        bordered_logo = Image.new("RGBA",
            (final_logo_size, final_logo_size),
            (255, 255, 255, 0)
        )

        mask_border = Image.new("L", (final_logo_size, final_logo_size), 0)
        draw_border = ImageDraw.Draw(mask_border)
        draw_border.ellipse((0, 0, final_logo_size, final_logo_size), fill=255)

        # Viền trắng
        draw_b = ImageDraw.Draw(bordered_logo)
        draw_b.ellipse((0, 0, final_logo_size, final_logo_size), fill=(255, 255, 255, 255))

        # Dán logo tròn vào giữa viền
        bordered_logo.paste(logo_round, (border_size, border_size), mask=mask)

        # === DÁN LOGO LÊN QR ===
        pos = (
            (qr_w - final_logo_size) // 2,
            (qr_h - final_logo_size) // 2
        )

        qr_img.paste(bordered_logo, pos, mask_border)

        # === THÊM LABEL BÊN DƯỚI ===
        qr_img = add_label_below_qr(qr_img, filename)

        save_qr_image(qr_img, filename, suffix="_with_logo")

    except Exception as e:
        print(f"\n❌ Lỗi tạo QR có logo: {e}")



# ================================
#               MENU
# ================================

def main():
    while True:
        print("\n==================================")
        print("     🛠️ MENU TẠO MÃ QR PYTHON 🛠️")
        print("==================================")
        print("1. Tạo Mã QR Cơ bản (URL/Text)")
        print("2. Tạo Mã QR Wi-Fi")
        print("3. Tạo Mã QR Tùy chỉnh Màu sắc")
        print("4. Tạo Mã QR Danh thiếp (VCard)")
        print("5. Tạo Mã QR Có Logo")
        print("6. Thoát")
        print("----------------------------------")

        choice = input("Nhập lựa chọn (1-6): ")

        if choice == '1':
            data = input("Nhập dữ liệu: ")
            filename = input("Nhập tên file: ")
            create_basic_qr(data, filename)

        elif choice == '2':
            create_wifi_qr()

        elif choice == '3':
            create_custom_qr()

        elif choice == '4':
            create_vcard_qr()

        elif choice == '5':
            create_qr_with_logo()

        elif choice == '6':
            print("Tạm biệt! 👋")
            sys.exit()

        else:
            print("❌ Lựa chọn không hợp lệ. Hãy nhập 1-6.")


# ================================
#          PROGRAM START
# ================================
if __name__ == "__main__":
    try:
        from PIL import Image
    except ImportError:
        print("\n❌ Bạn chưa cài Pillow. Hãy chạy: pip install Pillow")

    main()
