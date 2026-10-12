"""Retire reviewed artifacts only after validated v4 is published and selected."""
import json
from pathlib import Path
from collections import Counter

def read(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    published=read("data/validation/world-v4-published.json")
    assert published["complete"] and published["range_cors_verified"]
    assert published["base"]=="https://re.masahiko.info/nigiwai-topo/world/2026-09-15-v4/"
    config=Path("web/config.js").read_text(encoding="utf-8")
    assert published["base"] in config, "V4 is not selected in the frontend"
    validation=read("data/validation/held-density-release-v4.json")
    assert validation["complete"] and validation["all_index_leaf_peaks"]==319883
    assert validation["smeaton_peaks_within_1km"]==validation["sapezal_peaks_within_1km"]==0
    accounting=read("data/validation/world-v4-name-cohort-accounting.json")
    targets={"GeoNames:6149823":"53.491, -104.807", "GeoNames:6318630":"-12.989, -58.764"}
    assert set(accounting["absent_peak_keys"])==set(targets.values())
    prior=read("docs/unnamed-world-batch352-review.json")
    rows=[x for x in prior["items"] if x["decision"]=="hold"]
    assert len(rows)==21
    for ident,peak in targets.items():
        item=next(x for x in rows if x["id"]==ident)
        assert item["peak_keys"]==[peak]
        item.update(decision="resolved_density_removed", resolution_release="v4", resolution="Reviewed location quality hold; corrected artifact absent from assembled index; source retained; release published and selected.")
    queue=read("data/name-research/unnamed-world/remaining-review-queue.json")
    before=len(queue["items"])
    assert queue["remaining"]==before==accounting["remaining"]+len(targets)
    remaining=[x for x in queue["items"] if x["peak"] not in targets.values()]
    assert len(remaining)==accounting["remaining"]
    approvals=read("docs/unnamed-world-name-approvals.json")
    assert len(approvals["items"])==accounting["adopted"]
    summary=dict(prior["summary"])
    summary.update(remaining_candidate_peaks=sum(len(x["peak_keys"]) for x in rows if x["group"]=="new_candidates" and x["decision"]=="hold"),remaining_previous_holds=sum(x["group"]=="previous_holds" and x["decision"]=="hold" for x in rows),unnamed_remaining=len(remaining),resolved_by_density_rebuild=len(targets))
    assert summary["remaining_candidate_peaks"]==16 and summary["remaining_previous_holds"]==3
    queue.update(items=remaining,remaining=len(remaining),resolved_density_peaks=sorted(targets.values()),selected_world_root="data/distribution/foursquare-world-v4",priority_counts=dict(Counter(str(x["priority"]) for x in remaining)))
    save("docs/unnamed-world-v4-retirement-review.json",dict(snapshot=prior["snapshot"],summary=summary,items=rows))
    save("data/name-research/unnamed-world/remaining-review-queue.json",queue)
    print(summary)

if __name__=="__main__":main()
