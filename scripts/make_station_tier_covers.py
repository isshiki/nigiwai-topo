"""Render blog covers from the exact station Tier data, retaining every route station."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DATA = Path('web/station-tier-data.json')
OUT = Path('docs/assets/station-tier')
FONT = 'C:/Windows/Fonts/YuGothB.ttc'
TIERS = ['SS', 'S', 'A', 'B', 'C', 'D', 'none']
COLORS = ['#eeb7af', '#f0c99f', '#f0e3a5', '#cadfad', '#b9d8e7', '#d4d0e4', '#e4e8e1']


def font(size):
    return ImageFont.truetype(FONT, size)


def centered(draw, value, x, y, width, size, fill='#273b32'):
    f = font(size)
    while draw.textlength(value, font=f) > width and size > 17:
        size -= 1
        f = font(size)
    assert draw.textlength(value, font=f) <= width, value
    draw.text((x + width / 2, y), value, font=f, fill=fill, anchor='mt')


def render(route_id, title, filename, stations):
    selected = sorted([s for s in stations if any(l['id'] == route_id for l in s['lines'])], key=lambda s: (-(s['score'] if s['score'] is not None else -1), s['id']))
    assert selected and len({s['id'] for s in selected}) == len(selected)
    image = Image.new('RGB', (1600, 900), '#f7f8f3')
    draw = ImageDraw.Draw(image)
    draw.text((58, 34), '駅周辺のにぎわいでTier表を作ってみた', font=font(52), fill='#253d30')
    draw.text((60, 114), f'{title} · {len(selected)}駅', font=font(30), fill='#41694d')
    draw.text((1115, 125), 'あなたの駅は、何Tier？', font=font(25), fill='#41694d')
    counts = {}
    maximum_cards = max(sum((s['tier'] or 'none') == t for s in selected) for t in TIERS)
    card_width = min(190, (1528 - 174 - 8 * (maximum_cards - 1)) / maximum_cards)
    for i, (tier, color) in enumerate(zip(TIERS, COLORS)):
        rows = [s for s in selected if (s['tier'] or 'none') == tier]
        counts[tier] = len(rows)
        y = 183 + i * 86
        draw.rounded_rectangle((58, y, 1542, y + 78), radius=10, fill='white', outline='#d7dfd2', width=2)
        draw.rounded_rectangle((58, y, 160, y + 78), radius=10, fill=color)
        centered(draw, '峰なし' if tier == 'none' else tier, 58, y + 10, 102, 23 if tier == 'none' else 30)
        centered(draw, f'{len(rows)}駅', 58, y + 51, 102, 16)
        left, right, gap = 174, 1528, 8
        width = card_width
        for j, s in enumerate(rows):
            x = left + j * (width + gap)
            draw.rounded_rectangle((x, y + 8, x + width, y + 70), radius=6, fill='#fcfdfb', outline='#c3d2c0', width=1)
            # Draw a small train symbol directly; no font-dependent glyphs.
            draw.rounded_rectangle((x + 11, y + 14, x + 25, y + 28), radius=3, outline='#41694d', width=1)
            draw.rectangle((x + 14, y + 17, x + 22, y + 21), outline='#41694d', width=1)
            draw.line((x + 14, y + 28, x + 12, y + 31), fill='#41694d', width=1)
            draw.line((x + 22, y + 28, x + 24, y + 31), fill='#41694d', width=1)
            centered(draw, s['name'], x + 7, y + 31, width - 14, 23)
            centered(draw, '未判定' if s['score'] is None else f"{round(s['score']):,} 件/km²", x + 7, y + 57, width - 14, 13)
    draw.text((60, 810), '全国共通のTier · 地図の密度順 · 全駅掲載（峰なしは未判定）', font=font(20), fill='#4c6050')
    draw.text((60, 853), '登録の集まりを楽しむ地図です。実際の人出・人気の順位ではありません。', font=font(17), fill='#657466')
    draw.text((60, 875), 'POI: © 2026 Foursquare Labs, Inc. / Apache 2.0 · 駅: 国土数値情報 N02（CC BY 4.0）を加工', font=font(15), fill='#657466')
    output = OUT / filename
    image.save(output)
    return {'file': filename, 'route_id': route_id, 'display_title': title, 'station_count': len(selected), 'counts': counts, 'station_ids': [s['id'] for s in selected], 'width': 1600, 'height': 900}


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    OUT.mkdir(parents=True, exist_ok=True)
    covers = [render('東日本旅客鉄道 / 総武線', '総武線', 'cover-sobu.png', data['stations']),
              render('大阪市高速電気軌道 / 4号線(中央線)', '大阪メトロ 中央線', 'cover-osaka-chuo.png', data['stations'])]
    assert all(sum(c['counts'].values()) == c['station_count'] for c in covers)
    (OUT / 'metadata.json').write_text(json.dumps({'source_sha256': hashlib.sha256(DATA.read_bytes()).hexdigest(), 'snapshot': data['snapshot'], 'covers': covers}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(covers, ensure_ascii=True))


if __name__ == '__main__':
    main()
