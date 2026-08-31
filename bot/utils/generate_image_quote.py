import io
import os
import asyncio
from typing import Literal
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
import discord
import uuid

executor = ThreadPoolExecutor(max_workers=4)
FONT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'fonts', os.getenv("FONT"))
ANONYMOUS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images', 'anonymous.png')


def _apply_black_gradient_style_1(image: Image.Image) -> Image.Image:
    img = image.convert('RGBA')
    width, height = img.size
    black_layer = Image.new("RGBA", (width, height), (0, 0, 0, 255))

    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)

    start_x = 412
    fade_length = width - start_x

    for x in range(start_x, width):
        alpha = int(((x - start_x) / fade_length) * 255)
        mask_draw.line([(x, 0), (x, height)], fill=alpha)

    img.paste(black_layer, (0, 0), mask)
    return img


def _apply_black_gradient_style_2(image: Image.Image) -> Image.Image:
    img = image.convert('RGBA')
    width, height = image.size
    black_layer = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)

    fade_length = 100

    for i in range(0, fade_length):
        alpha = int((i / fade_length) * 255)
        mask_draw.line([(fade_length - i - 1, 0), (fade_length - i - 1, height)], fill=alpha)
        mask_draw.line([(width - fade_length + i, 0), (width - fade_length + i, height)], fill=alpha)
        mask_draw.line([(0, fade_length - i - 1), (width, fade_length - i - 1)], fill=alpha)
        mask_draw.line([(0, height - fade_length + i), (width, height - fade_length + i)], fill=alpha)

    img.paste(black_layer, (0, 0), mask)
    return img


def _merge_images(left_img: Image.Image, right_img: Image.Image):
    total_width = left_img.width + right_img.width
    max_height = max(left_img.height, right_img.height)
    combined_img = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 255))
    combined_img.paste(left_img, (0, 0))
    combined_img.paste(right_img, (left_img.width, 0))
    return combined_img


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width, draw: ImageDraw.ImageDraw) -> str:
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]

        if line_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)


def _draw_text_on_new_image(text: str, author: str) -> Image.Image:
    padding = 20
    width, height = 512, 512
    image_for_text = Image.new("RGBA", (width, height), 'black')
    draw = ImageDraw.Draw(image_for_text)

    text_font = ImageFont.truetype(FONT_PATH, size=20)
    author_font = ImageFont.truetype(FONT_PATH, size=15)
    text_color = (255, 255, 255, 255)

    wrapped_text = _wrap_text(text, text_font, width - (padding * 2), draw)

    center_x = width / 2
    center_y = height * 0.4

    draw.multiline_text(
        (center_x, center_y),
        wrapped_text,
        font=text_font,
        fill=text_color,
        anchor="ma",
        align='center'
    )

    text_bbox = draw.multiline_textbbox((center_x, center_y), wrapped_text, font=text_font, anchor="ma", align="center")
    text_bottom_y = text_bbox[3]
    spacing = 30
    author_text = f"~ {author}"

    draw.text(
        (center_x, text_bottom_y + spacing),
        author_text,
        font=author_font,
        fill=text_color,
        anchor="ma",
        align="center"
    )
    return image_for_text


def _adjust_image_size(image: Image.Image) -> Image.Image:
    width, height = image.size
    if width != 512 or height != 512:
        return image.resize((512, 512))
    return image


def _process_image_quote(text: str, author: str, image_bytes: bytes, style: Literal[1, 2, None]):
    image = Image.open(io.BytesIO(image_bytes))
    image = _adjust_image_size(image)
    image = image.convert('L')

    if style == 1 or style == None:
        image = _apply_black_gradient_style_1(image)
    elif style == 2:
        image = _apply_black_gradient_style_2(image)
    text_image = _draw_text_on_new_image(text, author)
    merged_image = _merge_images(image, text_image)
    output_buffer = io.BytesIO()
    merged_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)
    return output_buffer


def _get_anonymous() -> bytes:
    with open(ANONYMOUS_PATH, "rb") as f:
        return f.read()


async def generate_image_quote(text: str, author: str, image: discord.Asset, style: Literal[1, 2, None]):
    loop = asyncio.get_running_loop()

    if not image:
        data = await loop.run_in_executor(
            executor,
            _get_anonymous
        )
    else:
        data = await image.with_size(512).read()
    
    image = await loop.run_in_executor(
        executor,
        _process_image_quote,
        text,
        author,
        data,
        style
    )

    return discord.File(fp=image, filename=f"{author}_{uuid.uuid4()}.png")
    