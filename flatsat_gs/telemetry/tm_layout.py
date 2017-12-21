import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta

from telemetry import TelemetryView, FileView, MAX_TELEMETRY_IN_FILE, MAX_FILE_TIME_SPAN

timestamp = datetime.now() - timedelta(hours=1)

base_view = TelemetryView(timestamp, 1000, MAX_TELEMETRY_IN_FILE)

from PIL import Image, ImageDraw, ImageFont

FileLabelFont = ImageFont.truetype('arial.ttf', 30, encoding="unic")
DateLabelFont = ImageFont.truetype('arial.ttf', 25, encoding="unic")
ChunksCountLabelFont = ImageFont.truetype('arial.ttf', 20, encoding="unic")


def date_format(dt):
    # type: (datetime) -> str

    return dt.strftime('%Y-%m-%d %H:%M:%S')


def center_box(box_size, container_coords):
    (c_left, c_right) = container_coords

    (b_w, b_h) = box_size

    container_center = (c_right - c_left) / 2

    return c_left + container_center - b_w / 2


def draw_telemetry_file(start, height, draw, file_view, label):
    # type: (int, int, ImageDraw.ImageDraw, FileView) -> None

    (img_w, img_h) = draw.im.size

    SIDE_PADDING = 50

    (label_w, label_h) = draw.textsize(text=label, font=FileLabelFont)

    label_pos = center_box(draw.textsize(text=label, font=FileLabelFont), (SIDE_PADDING, img_w - SIDE_PADDING))

    draw.text(text=label, xy=(label_pos, start), fill='green', font=FileLabelFont)

    rect_top = start + label_h + 5
    rect_bottom = start + label_h + 5 + height

    draw.rectangle([(SIDE_PADDING, rect_top), (img_w - SIDE_PADDING, rect_bottom)],
                   outline='black', fill=None)

    date_labels_y = start + label_h + 5 + height

    draw.text(text=date_format(file_view.first_entry), font=DateLabelFont, fill='black',
              xy=(SIDE_PADDING, start))

    (last_entry_w, _) = draw.textsize(text=date_format(file_view.last_entry), font=DateLabelFont)

    last_entry_x = SIDE_PADDING + (img_w - 2 * SIDE_PADDING) / float(MAX_TELEMETRY_IN_FILE) * file_view.chunks

    draw.line(xy=[(last_entry_x, rect_top), (last_entry_x, rect_bottom)], fill='blue', width=5)

    draw.rectangle(xy=[(SIDE_PADDING, rect_top), (last_entry_x, rect_bottom)], fill='LightBlue', outline='black')

    if file_view.chunks > 0.5 * MAX_TELEMETRY_IN_FILE:
        last_entry_x = last_entry_x - last_entry_w

    draw.text(text=date_format(file_view.last_entry), font=DateLabelFont, fill='black',
              xy=(last_entry_x, date_labels_y + 5))

    (estimated_end_w, _) = draw.textsize(text=date_format(file_view.estimated_file_end), font=DateLabelFont)

    draw.text(text=date_format(file_view.estimated_file_end), font=DateLabelFont, fill='black',
              xy=(img_w - SIDE_PADDING - estimated_end_w, rect_bottom + 5))

    now = datetime.now()

    if file_view.first_entry <= now <= file_view.estimated_file_end:
        in_file_time_offset = now - file_view.first_entry

        now_x = SIDE_PADDING + (img_w - 2 * SIDE_PADDING) * in_file_time_offset.total_seconds() / MAX_FILE_TIME_SPAN.total_seconds()

        draw.line(xy=[(now_x, rect_top), (now_x, rect_bottom)], fill='red', width=5)


img = Image.new(mode='RGB', size=(1920, 1080), color='white')

draw = ImageDraw.Draw(img)

(w, h) = draw.im.size

draw_telemetry_file(50, int(0.3 * h), draw, base_view.current_file_view, 'telemetry.current')

draw_telemetry_file(50 + int(0.5 * h), int(0.3 * h), draw, base_view.previous_file_view, 'telemetry.previous')

del draw

img.save('D:/tmp/tm.jpg', 'JPEG')
