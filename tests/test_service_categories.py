import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from fetch_foursquare import classify_category


class ServiceCategoryTests(unittest.TestCase):
    def test_service_uses_hierarchy_not_accidental_name_substrings(self):
        for name in ['Barber Shop', 'Laundry Service', 'Computer Repair Service']:
            self.assertEqual(classify_category({'category_name': name,
                'level1_category_name': 'Business and Professional Services'}), 'service')
        self.assertEqual(classify_category({'category_name': 'Physician',
            'level1_category_name': 'Health and Medicine'}), 'service')
        self.assertEqual(classify_category({'category_name': 'Bar',
            'level1_category_name': 'Dining and Drinking'}), 'food')
        self.assertEqual(classify_category({'category_name': 'Grocery Store',
            'level1_category_name': 'Retail'}), 'shopping')
