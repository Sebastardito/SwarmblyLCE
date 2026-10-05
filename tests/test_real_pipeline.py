"""End-to-end test of run_real and decide against a local fake OpenAI-compatible server.

The server answers with MockBackend, so this checks plumbing, guards and the
decision code, never model behaviour.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from swarmbly_lce.backends import MockBackend
from lce_validation import decide as D
from lce_validation import experiments as E
from lce_validation import mcq as M
from lce_validation import run_real


class _Handler(BaseHTTPRequestHandler):
    mocks: dict[str, MockBackend] = {}

    def log_message(self, *a):  # silence
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.endswith("/api/version"):
            self._send({"version": "fake"})
        elif self.path.endswith("/api/tags"):
            self._send({"models": [{"name": m, "digest": "sha256:fake"} for m in self.mocks]})
        else:
            self.send_error(404)

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path.endswith("/chat/completions"):
            fam = req["model"].split(":")[0]
            mb = self.mocks.setdefault(req["model"], MockBackend(family=fam))
            text = mb.generate(req["messages"][0]["content"], temperature=req.get("temperature", 0), seed=req.get("seed", 0))
            self._send({"choices": [{"message": {"content": text}}]})
        elif self.path.endswith("/embeddings"):
            vecs = MockBackend().embed(req["input"])
            self._send({"data": [{"embedding": list(map(float, v))} for v in vecs]})
        else:
            self.send_error(404)


@pytest.fixture()
def server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/v1"
    srv.shutdown()


def test_run_real_exploratory_end_to_end(server, tmp_path):
    rc = run_real.main(["--url", server, "--models", "fama:1b,famb:1b,famc:1b", "--embed-model", "emb",
                        "--mcq", str(E.FIXTURES / "mcq_synthetic.json"), "--out", str(tmp_path)])
    assert rc == 0
    res = json.loads((tmp_path / "results_real.json").read_text())
    assert res["header"]["backend_kind"] == "real"
    assert res["header"]["confirmatory"] is False          # no pre-registration given
    assert res["header"]["mcq_sha256"] == M.file_sha256(E.FIXTURES / "mcq_synthetic.json")
    assert "raw" in res["C2"] and res["C2"]["raw"]["mcq_without"]
    v = res["verdicts"]
    assert v["global_refusals"]
    assert all(r["verdict"] in {"exploratory_only", "refused", "not_tested"} for k, r in v.items() if isinstance(r, dict) and "verdict" in r)
    assert (tmp_path / "REPORT_REAL.md").read_text().startswith("# lce_validation — real-model run")


def test_run_real_refuses_missing_mcq(server, tmp_path):
    assert run_real.main(["--url", server, "--models", "fama:1b,famb:1b", "--mcq", str(tmp_path / "none.json"), "--out", str(tmp_path)]) == 2


def test_homogeneity_refuses_temperature_zero():
    fam = [MockBackend(family=f) for f in ("a", "b", "c")]
    with pytest.raises(ValueError):
        E.c2_projection(fam, MockBackend(), temperature=0.0, bootstrap_B=100)


def _res(**c2):
    base = {"header": {"confirmatory": True, "embed_model": "nomic-embed-text", "distinct_families": 3},
            "build_wiki": {"claims": 13}, "C1": {"acc_with_memory": 0.9, "acc_without_memory": 0.0, "gain": 0.9},
            "C2": {"lexicon": {"difference": 0.5, "difference_ci95": [0.3, 0.7]},
                   "homogeneity": {"reduction_projection": 0.05, "reduction_projection_ci95": [0.02, 0.08],
                                   "projection_beyond_placebo_ci95": [0.01, 0.03]},
                   "error_agreement": {"delta": 0.01, "delta_ci95": [-0.05, 0.07], "jointly_wrong_with": 500,
                                       "jointly_wrong_without": 500, "invalid_rate_with": 0.0, "invalid_rate_without": 0.0,
                                       "excess_ci95": [0.1, 0.2]}}}
    for k, v in c2.items():
        base["C2"][k].update(v)
    return base


def test_decide_rules():
    v = D.decide(_res())
    assert v["C1"]["verdict"] == "holds" and v["H-C2_lexicon"]["verdict"] == "holds"
    assert v["H-C17a"]["verdict"] == "holds" and v["H-C17b"]["verdict"] == "holds"
    assert v["H-C2_rho"]["verdict"] == "not_tested"
    v = D.decide(_res(error_agreement={"delta": 0.2, "delta_ci95": [0.12, 0.28]}))
    assert v["H-C17b"]["verdict"] == "falsified"
    v = D.decide(_res(error_agreement={"delta": 0.05, "delta_ci95": [-0.03, 0.13]}))
    assert v["H-C17b"]["verdict"] == "inconclusive"
    v = D.decide(_res(error_agreement={"jointly_wrong_with": 50}))
    assert v["H-C17b"]["verdict"] == "refused"
    v = D.decide(_res(homogeneity={"reduction_projection": -0.01, "reduction_projection_ci95": [-0.03, 0.01]}))
    assert v["H-C17a"]["verdict"] == "falsified"
    v = D.decide(_res(homogeneity={"projection_beyond_placebo_ci95": [-0.01, 0.02]}))
    assert "NOT shown" in v["H-C17a"]["qualification"]
    r = _res(); r["header"]["confirmatory"] = False
    assert D.decide(r)["H-C17a"]["verdict"] == "exploratory_only"


def test_mcq_parse_and_chance():
    assert M.parse_letter("B") == "B" and M.parse_letter("The answer is C.") == "C" and M.parse_letter("none") is None
    items = M.load_items(E.FIXTURES / "mcq_synthetic.json")
    assert len(items) == 60 and all(it.answer in "ABCD" for it in items)
    p = M.mcq_prompt(items[0], "register: formal")
    assert p.startswith(M.MCQ_MARKER) and "STYLE: register: formal" in p and "D. " in p
