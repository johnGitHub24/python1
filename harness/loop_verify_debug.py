"""
Harness & Loop Engineering
==========================
循環：Loop → Verify → Debug

【設計目標】
1. Loop：重複執行同一組驗證命令（pytest）
2. Verify：彙整通過 / 失敗、覆蓋率、退出碼
3. Debug：失敗時輸出精簡診斷與建議下一步

用法：
  python harness/loop_verify_debug.py
  python harness/loop_verify_debug.py --max-loops 3 --unit-only
  python harness/loop_verify_debug.py --once
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "out" / "harness"


@dataclass
class LoopResult:
    """單次 loop 的驗證結果。"""

    loop_index: int
    started_at: str
    elapsed_sec: float
    exit_code: int
    passed: bool
    command: list[str]
    stdout_tail: str = ""
    stderr_tail: str = ""
    hints: list[str] = field(default_factory=list)


def _tail(text: str, lines: int = 40) -> str:
    parts = text.strip().splitlines()
    return "\n".join(parts[-lines:])


def _debug_hints(stdout: str, stderr: str, exit_code: int) -> list[str]:
    """
    【Debug 階段】依常見失敗模式給出提示。
    這不是自動修 bug，而是縮小排查範圍。
    """
    blob = (stdout + "\n" + stderr).lower()
    hints: list[str] = []
    if exit_code == 0:
        hints.append("全部通過：可進入下一功能，或提高覆蓋率門檻。")
        return hints
    if "modulenotfounderror" in blob or "no module named" in blob:
        hints.append("缺少套件：執行 pip install -r requirements.txt")
    if "assertionerror" in blob:
        hints.append("斷言失敗：比對 expected/actual，檢查 parser 或 fixture。")
    if "connection" in blob or "timed out" in blob:
        hints.append("網路相關：整合測試應使用本機 HTTPServer，勿依賴外網。")
    if "permission" in blob:
        hints.append("權限問題：確認 out/ 目錄可寫入。")
    if not hints:
        hints.append("查看上方失敗 traceback；優先修第一個失敗測試再重跑。")
    hints.append("建議：先 pytest -m unit，通過後再跑 integration。")
    return hints


def run_verify(command: list[str], loop_index: int) -> LoopResult:
    """【Verify】執行測試並收集結果。"""
    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = time.perf_counter() - t0
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    return LoopResult(
        loop_index=loop_index,
        started_at=started.isoformat(),
        elapsed_sec=round(elapsed, 3),
        exit_code=proc.returncode,
        passed=proc.returncode == 0,
        command=command,
        stdout_tail=_tail(stdout),
        stderr_tail=_tail(stderr),
        hints=_debug_hints(stdout, stderr, proc.returncode),
    )


def print_result(result: LoopResult) -> None:
    status = "PASS" if result.passed else "FAIL"
    print("=" * 60)
    print(f"[Loop #{result.loop_index}] {status}  ({result.elapsed_sec}s)")
    print(f"CMD: {' '.join(result.command)}")
    if result.stdout_tail:
        print("--- stdout (tail) ---")
        print(result.stdout_tail)
    if result.stderr_tail:
        print("--- stderr (tail) ---")
        print(result.stderr_tail)
    print("--- debug hints ---")
    for hint in result.hints:
        print(f"  * {hint}")
    print("=" * 60)


def save_report(results: list[LoopResult]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / "last_run.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "loops": [asdict(r) for r in results],
        "final_passed": bool(results and results[-1].passed),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_pytest_cmd(args: argparse.Namespace) -> list[str]:
    cmd = [sys.executable, "-m", "pytest"]
    if args.unit_only:
        cmd += ["-m", "unit"]
    elif args.integration_only:
        cmd += ["-m", "integration"]
    if args.cov:
        cmd += ["--cov=src/news_scraper", "--cov-report=term-missing"]
    return cmd


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Loop → Verify → Debug harness")
    p.add_argument("--max-loops", type=int, default=1, help="最多迴圈次數（失敗可重試）")
    p.add_argument("--once", action="store_true", help="只跑一次（等同 --max-loops 1）")
    p.add_argument("--sleep", type=float, default=0.0, help="每次 loop 間隔秒數")
    p.add_argument("--unit-only", action="store_true", help="只跑單元測試")
    p.add_argument("--integration-only", action="store_true", help="只跑整合測試")
    p.add_argument("--cov", action="store_true", help="附帶覆蓋率")
    p.add_argument(
        "--stop-on-pass",
        action="store_true",
        default=True,
        help="通過即停止（預設開啟）",
    )
    p.add_argument(
        "--no-stop-on-pass",
        action="store_false",
        dest="stop_on_pass",
        help="通過後仍跑滿 max-loops",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    max_loops = 1 if args.once else max(1, args.max_loops)
    command = build_pytest_cmd(args)
    results: list[LoopResult] = []

    print("Harness 啟動：Loop → Verify → Debug")
    print(f"工作目錄: {ROOT}")
    print(f"最大迴圈: {max_loops}")

    final_code = 1
    for i in range(1, max_loops + 1):
        result = run_verify(command, i)
        results.append(result)
        print_result(result)
        final_code = result.exit_code
        if result.passed and args.stop_on_pass:
            break
        if i < max_loops and args.sleep > 0:
            time.sleep(args.sleep)

    report = save_report(results)
    print(f"報告已寫入: {report}")
    return final_code


if __name__ == "__main__":
    raise SystemExit(main())
