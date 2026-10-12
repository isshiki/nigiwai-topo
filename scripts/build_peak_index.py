"""Build a viewport index: complete leaves and top-100 summaries per node.

Fully covered nodes suffice for exact top-20 ranking. Partial intersections
must descend to leaves; summaries alone are never used at viewport edges.
"""
import argparse
import json
from pathlib import Path


def build_index(features, leaf_size=256):
    if leaf_size < 1:
        raise ValueError('leaf_size must be positive')
    nodes = []

    def build(items, depth=0):
        coords = [f['geometry']['coordinates'] for f in items]
        bbox = [min(c[0] for c in coords), min(c[1] for c in coords),
                max(c[0] for c in coords), max(c[1] for c in coords)]
        node_id = len(nodes)
        node = {'bbox': bbox, 'count': len(items)}
        nodes.append(node)
        ordered = sorted(items, key=lambda f: -f['properties']['density'])
        if len(items) <= leaf_size:
            node['features'] = ordered
        else:
            # Median split guarantees progress even for identical coordinates.
            axis = depth % 2
            items = sorted(items, key=lambda f: f['geometry']['coordinates'][axis])
            mid = len(items)//2
            node['top'] = ordered[:100]
            node['children'] = [build(items[:mid], depth+1), build(items[mid:], depth+1)]
        return node_id

    root = build(features) if features else None
    return {'version': 1, 'root': root, 'nodes': nodes}


def query_index(index, bbox, limit=20, floor=800):
    """Reference query for a non-wrapping bbox; split date-line viewports first."""
    if not 1 <= limit <= 100:
        raise ValueError('Summary query supports limits 1..100')
    west, south, east, north = bbox
    candidates = []

    def visit(node_id):
        node = index['nodes'][node_id]
        a, b, c, d = node['bbox']
        if c < west or a > east or d < south or b > north:
            return
        contained = west <= a and c <= east and south <= b and d <= north
        if 'features' in node or contained:
            for f in node.get('features', node.get('top', [])):
                lon, lat = f['geometry']['coordinates']
                if west <= lon <= east and south <= lat <= north and f['properties']['density'] >= floor:
                    candidates.append(f)
        else:
            for child in node['children']:
                visit(child)

    if index['root'] is not None:
        visit(index['root'])
    return sorted(candidates, key=lambda f: -f['properties']['density'])[:limit]


def write_index(features, output):
    index = build_index(features)
    output.mkdir(parents=True, exist_ok=True)
    for i, node in enumerate(index['nodes']):
        (output/f'{i}.json').write_text(json.dumps(node, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    (output/'index.json').write_text(json.dumps({'version': 1, 'root': index['root'], 'count': len(features), 'node_count':len(index['nodes']),
        'node_file_template': '{id}.json', 'summary_limit': 100}, separators=(',', ':')), encoding='utf-8')
    print(f'peaks={len(features)} nodes={len(index["nodes"])}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8'))
    write_index([f for f in data['features'] if f['properties'].get('kind') == 'peak'],args.output)


if __name__ == '__main__':
    main()
