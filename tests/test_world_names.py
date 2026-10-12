import unittest
from scripts.world_names import reference_records, WorldNamer
from scripts.regional_grid import RegionalGrid
from scripts.build_national import surface


def element(i, lon, name='Central', **tags):
    return {'type':'node','id':i,'lon':lon,'lat':0,'tags':{'name':name,'railway':'station',**tags}}


class WorldNamesTests(unittest.TestCase):
    def test_duplicate_station_representations_and_excluded_platforms(self):
        stations, _ = reference_records([element(1,0),element(2,.001),element(3,.02),
            element(4,0,railway='platform'),element(5,0,disused='yes'),
            element(6,0,passenger='no')])
        self.assertEqual(len(stations),2)
        self.assertEqual(stations[0]['osm_ids'],['node/1','node/2'])

    def test_merge_does_not_chain_along_a_long_line(self):
        stations, _ = reference_records([element(i,i*.002) for i in range(3)])
        self.assertEqual(len(stations),2)

    def test_name_priority_station_radius_and_settlement_fallback(self):
        stations, places = reference_records([element(1,0,**{'name:ja':'中央駅'}),
            {'type':'node','id':2,'lon':.03,'lat':0,'tags':{'place':'city','name':'City'}}])
        namer = WorldNamer(stations,places)
        self.assertEqual(namer(0,0)['name'],'中央駅')
        result = namer(.03,0)
        self.assertEqual(result['name'],'City付近')
        self.assertGreater(result['station_distance_m'],1500)
        self.assertEqual(namer(-80,-30)['name'],'30.00°S 80.00°W')
        self.assertEqual(WorldNamer([],[])(1,1)['name_source'],'coordinates')

    def test_regional_density_surface_invokes_world_namer(self):
        grid = RegionalGrid(-.12,51.5)
        lon, lat = grid.inverse.transform(20000,20000)
        namer = WorldNamer([{'name':'Example','lon':lon,'lat':lat,'osm_ids':['node/1'],'name_key':'name'}],[])
        geo = surface([{'x':20000,'y':20000}]*30,0,0,200,None,[],inverse=grid.inverse,namer=namer)
        peaks = [f for f in geo['features'] if f['properties']['kind']=='peak']
        self.assertEqual(len(peaks),1)
        self.assertEqual(peaks[0]['properties']['name'],'Example')
        self.assertAlmostEqual(peaks[0]['geometry']['coordinates'][0],lon,places=5)
